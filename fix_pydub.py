import sys


# Создаём заглушку для audioop
class AudioopStub:
    def __getattr__(self, name):
        def stub(*args, **kwargs):
            if name in ("getsample", "max", "maxpp", "rms", "avg", "avgpp"):
                return 0
            if name in ("ratecv",):
                return b"", 0
            return b""

        return stub


# Подменяем модули ДО импорта pydub
sys.modules["audioop"] = AudioopStub()
sys.modules["pyaudioop"] = AudioopStub()

print("✅ Audioop заглушка установлена")
