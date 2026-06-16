cmake_minimum_required(VERSION 3.16)
project(wro2026 CXX)

set(CMAKE_CXX_STANDARD 17)

# --- robot (Raspberry Pi / pigpio) ---
find_library(WIRINGPI_LIB wiringPi
    PATHS ${CMAKE_CURRENT_SOURCE_DIR}/vendor/wiringpi
    NO_DEFAULT_PATH
)
if(NOT WIRINGPI_LIB)
    message(FATAL_ERROR
        "WiringPi library not found.\n"
        "Másold át a Pi-ről (egyszer kell):\n"
        "  mkdir -p cpp/vendor/wiringpi\n"
        "  scp jedlikpi@jedlikpi.local:/usr/lib/libwiringPi.so  cpp/vendor/wiringpi/\n"
        "  scp jedlikpi@jedlikpi.local:/usr/include/wiringPi.h  cpp/vendor/wiringpi/"
    )
endif()

add_library(robot SHARED
    src/stepper_motor.cpp
    src/mpu6050.cpp
    src/robot.cpp
    src/robot_c_api.cpp
)
target_include_directories(robot PUBLIC include/ vendor/wiringpi/)
target_link_libraries(robot PRIVATE ${WIRINGPI_LIB} pthread)
set_target_properties(robot PROPERTIES
    OUTPUT_NAME "robot"
    PREFIX      "lib"
    SUFFIX      ".so"
)
