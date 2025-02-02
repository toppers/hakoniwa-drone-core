# Androidプラットフォームの設定
set(CMAKE_SYSTEM_NAME Android)
set(CMAKE_ANDROID_NDK $ENV{ANDROID_NDK_HOME})  # 環境変数からNDKパスを取得
set(CMAKE_ANDROID_API 21)                     # APIレベル
set(CMAKE_ANDROID_ARCH_ABI arm64-v8a)         # ターゲットABI
set(ANDROID_BUILD ON)

# Androidツールチェインファイルを明示的に指定
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_ANDROID_NDK}/build/cmake/android.toolchain.cmake")

# C標準とフラグ
set(CMAKE_C_FLAGS "-std=gnu99")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wunknown-pragmas")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wmissing-prototypes")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wtrigraphs")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wimplicit-int")

# C++標準とフラグ
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wextra")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-long-long")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pedantic")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
