import ctypes
from ctypes import wintypes
from pathlib import Path
import sys
import threading
import pygame

class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

def _make_guid(l: int, w1: int, w2: int, b1: int, b2: int, b3: int, b4: int, b5: int, b6: int, b7: int, b8: int) -> GUID:
    g = GUID()
    g.Data1 = l
    g.Data2 = w1
    g.Data3 = w2
    g.Data4 = (ctypes.c_ubyte * 8)(b1, b2, b3, b4, b5, b6, b7, b8)
    return g

MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING = _make_guid(0xfb394f3d, 0xccf1, 0x42ee, 0xbb, 0xb3, 0xf9, 0xb8, 0x45, 0xd5, 0x68, 0x1d)
MF_MT_MAJOR_TYPE = _make_guid(0x48eba18e, 0xf8c9, 0x4687, 0xbf, 0x11, 0x0a, 0x74, 0xc9, 0xf9, 0x6a, 0x8f)
MFMediaType_Video = _make_guid(0x73646976, 0x0000, 0x0010, 0x80, 0x00, 0x00, 0xaa, 0x00, 0x38, 0x9b, 0x71)
MF_MT_SUBTYPE = _make_guid(0xf7e34c9a, 0x42e8, 0x4714, 0xb7, 0x4b, 0xcb, 0x29, 0xd7, 0x2c, 0x35, 0xe5)
MFVideoFormat_RGB32 = _make_guid(22, 0x0000, 0x0010, 0x80, 0x00, 0x00, 0xaa, 0x00, 0x38, 0x9b, 0x71)
MF_MT_FRAME_SIZE = _make_guid(0x1652c33d, 0xd6b2, 0x4012, 0xb8, 0x34, 0x72, 0x03, 0x08, 0x49, 0xa3, 0x7d)

class COMObject(ctypes.Structure):
    pass
COMObject._fields_ = [("lpVtbl", ctypes.POINTER(ctypes.c_void_p))]
PCOMObject = ctypes.POINTER(COMObject)
PPCOMObject = ctypes.POINTER(PCOMObject)

def _call_com(obj: PCOMObject, idx: int, restype: type, *argtypes: type) -> object:
    fn_ptr = obj.contents.lpVtbl[idx]
    proto = ctypes.WINFUNCTYPE(restype, PCOMObject, *argtypes)
    return proto(fn_ptr)

def _release_com(obj: PCOMObject | None) -> None:
    if obj:
        _call_com(obj, 2, ctypes.c_ulong)(obj)

_MF_INITIALIZED: bool = False
_MF_LOCK: threading.Lock = threading.Lock()
_THREAD_LOCAL: threading.local = threading.local()

def init_media_foundation() -> None:
    global _MF_INITIALIZED
    if sys.platform != "win32":
        return
    if not getattr(_THREAD_LOCAL, "com_initialized", False):
        ctypes.windll.ole32.CoInitializeEx(None, 0)
        _THREAD_LOCAL.com_initialized = True
    with _MF_LOCK:
        if not _MF_INITIALIZED:
            hr = ctypes.windll.mfplat.MFStartup(0x00020070, 1)
            if hr != 0:
                raise RuntimeError(f"CRITICAL: Failed to initialize Media Foundation, hr={hex(hr & 0xFFFFFFFF)}")
            _MF_INITIALIZED = True


# Maps near-white video background values (245..255) to pure 255 so the video border blends
# invisibly into the (255, 255, 255) screen background (applied before and after smoothscale by design).
_COLOR_LEVEL_TABLE: bytes = bytes(min(255, int(i * 255 / 245)) if i < 245 else 255 for i in range(256))


class WMFVideoReader:
    def __init__(self, video_path: Path) -> None:
        self._reader: PCOMObject | None = None
        self._sample: PCOMObject | None = None
        self._buffer: PCOMObject | None = None
        self._width: int = 0
        self._height: int = 0
        self._is_eof: bool = False

        if not isinstance(video_path, Path):
            raise TypeError(f"CRITICAL: video_path must be a Path, got {type(video_path).__name__}")
        if not video_path.is_file():
            raise FileNotFoundError(f"CRITICAL: Video file not found at {video_path}")
        if sys.platform != "win32":
            raise RuntimeError("CRITICAL: WMFVideoReader requires Windows OS")

        init_media_foundation()
        self.video_path: Path = video_path

        self._init_reader()

    def _init_reader(self) -> None:
        mfplat = ctypes.windll.mfplat
        mfreadwrite = ctypes.windll.mfreadwrite

        pAttr = PCOMObject()
        hr = mfplat.MFCreateAttributes(ctypes.byref(pAttr), 1)
        if hr != 0:
            raise RuntimeError(f"CRITICAL: MFCreateAttributes failed, hr={hex(hr & 0xFFFFFFFF)}")

        set_uint32 = _call_com(pAttr, 21, ctypes.c_int32, ctypes.POINTER(GUID), wintypes.UINT)
        set_uint32(pAttr, ctypes.byref(MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING), 1)

        pReader = PCOMObject()
        abs_path = str(self.video_path.resolve())
        hr = mfreadwrite.MFCreateSourceReaderFromURL(abs_path, pAttr, ctypes.byref(pReader))
        _release_com(pAttr)
        if hr != 0:
            raise RuntimeError(f"CRITICAL: MFCreateSourceReaderFromURL failed for {abs_path}, hr={hex(hr & 0xFFFFFFFF)}")

        pMediaType = PCOMObject()
        hr = mfplat.MFCreateMediaType(ctypes.byref(pMediaType))
        if hr != 0:
            _release_com(pReader)
            raise RuntimeError(f"CRITICAL: MFCreateMediaType failed, hr={hex(hr & 0xFFFFFFFF)}")

        set_guid = _call_com(pMediaType, 24, ctypes.c_int32, ctypes.POINTER(GUID), ctypes.POINTER(GUID))
        set_guid(pMediaType, ctypes.byref(MF_MT_MAJOR_TYPE), ctypes.byref(MFMediaType_Video))
        set_guid(pMediaType, ctypes.byref(MF_MT_SUBTYPE), ctypes.byref(MFVideoFormat_RGB32))

        set_current_type = _call_com(pReader, 7, ctypes.c_int32, wintypes.DWORD, ctypes.c_void_p, PCOMObject)
        hr = set_current_type(pReader, 0xFFFFFFFC, None, pMediaType)
        _release_com(pMediaType)
        if hr != 0:
            _release_com(pReader)
            raise RuntimeError(f"CRITICAL: SetCurrentMediaType RGB32 failed, hr={hex(hr & 0xFFFFFFFF)}")

        pOutType = PCOMObject()
        get_current_type = _call_com(pReader, 6, ctypes.c_int32, wintypes.DWORD, PPCOMObject)
        hr = get_current_type(pReader, 0xFFFFFFFC, ctypes.byref(pOutType))
        if hr == 0 and pOutType:
            get_uint64 = _call_com(pOutType, 8, ctypes.c_int32, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_uint64))
            packed_size = ctypes.c_uint64()
            hr_s = get_uint64(pOutType, ctypes.byref(MF_MT_FRAME_SIZE), ctypes.byref(packed_size))
            if hr_s == 0:
                self._width = int(packed_size.value >> 32)
                self._height = int(packed_size.value & 0xFFFFFFFF)
            _release_com(pOutType)

        if self._width == 0 or self._height == 0:
            pNative = PCOMObject()
            get_native_type = _call_com(pReader, 5, ctypes.c_int32, wintypes.DWORD, wintypes.DWORD, PPCOMObject)
            hr_n = get_native_type(pReader, 0xFFFFFFFC, 0, ctypes.byref(pNative))
            if hr_n == 0 and pNative:
                get_uint64_n = _call_com(pNative, 8, ctypes.c_int32, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_uint64))
                packed_size_n = ctypes.c_uint64()
                hr_sn = get_uint64_n(pNative, ctypes.byref(MF_MT_FRAME_SIZE), ctypes.byref(packed_size_n))
                if hr_sn == 0:
                    self._width = int(packed_size_n.value >> 32)
                    self._height = int(packed_size_n.value & 0xFFFFFFFF)
                _release_com(pNative)

        self._reader = pReader

    def get_dimensions(self) -> tuple[int, int]:
        return self._width, self._height

    def read_frame_surface(self) -> pygame.Surface | None:
        if self._reader is None or self._is_eof:
            return None

        read_sample = _call_com(self._reader, 9, ctypes.c_int32, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(ctypes.c_int64), PPCOMObject)
        actStream = wintypes.DWORD()
        flags = wintypes.DWORD()
        timestamp = ctypes.c_int64()
        pSample = PCOMObject()

        while True:
            hr = read_sample(self._reader, 0xFFFFFFFC, 0, ctypes.byref(actStream), ctypes.byref(flags), ctypes.byref(timestamp), ctypes.byref(pSample))
            # MF_SOURCE_READERF_ERROR = 0x01, MF_SOURCE_READERF_ENDOFSTREAM = 0x02
            if hr != 0 or (flags.value & 0x02) or (flags.value & 0x01):
                self._is_eof = True
                return None
            if pSample:
                break
            # If no sample and stream tick / gap, loop until next sample or EOF


        pBuffer = PCOMObject()
        to_contiguous = _call_com(pSample, 41, ctypes.c_int32, PPCOMObject)
        hr = to_contiguous(pSample, ctypes.byref(pBuffer))
        if hr != 0 or not pBuffer:
            _release_com(pSample)
            return None

        lock_buf = _call_com(pBuffer, 3, ctypes.c_int32, ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD))
        unlock_buf = _call_com(pBuffer, 4, ctypes.c_int32)
        pData = ctypes.POINTER(ctypes.c_ubyte)()
        maxLen = wintypes.DWORD()
        curLen = wintypes.DWORD()
        hr = lock_buf(pBuffer, ctypes.byref(pData), ctypes.byref(maxLen), ctypes.byref(curLen))
        if hr != 0:
            _release_com(pBuffer)
            _release_com(pSample)
            return None

        raw_bytes = ctypes.string_at(pData, curLen.value)
        unlock_buf(pBuffer)
        _release_com(pBuffer)
        _release_com(pSample)

        expected_bytes = self._width * self._height * 4
        if len(raw_bytes) != expected_bytes:
            return None

        surf = pygame.Surface((self._width, self._height), depth=32, masks=(0x00FF0000, 0x0000FF00, 0x000000FF, 0))
        surf.get_buffer().write(raw_bytes.translate(_COLOR_LEVEL_TABLE))
        return surf

    def close(self) -> None:
        if getattr(self, "_reader", None) is not None:
            _release_com(self._reader)
            self._reader = None

    def __del__(self) -> None:
        self.close()
