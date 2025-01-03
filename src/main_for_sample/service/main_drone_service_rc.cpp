#include "service/drone/drone_service_rc_api.h"
#include <iostream>
#include <thread>
#include <sstream>
#include <vector>
#include <string>
#include <queue>
#include <iomanip>


int main(int argc, const char* argv[])
{
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << "<real_sleep_msec> <drone_config_dir_path>" << std::endl;
        return 1;
    }
    int real_sleep_msec = std::stoi(argv[1]);
    const char* drone_config_dir_path = argv[2];

    int ret = drone_service_rc_init(drone_config_dir_path, nullptr, true);
    if (ret != 0) {
        std::cerr << "Failed to initialize drone service" << std::endl;
        return 1;
    }

    ret = drone_service_rc_start();
    std::queue<char> queue_keyboard;
    std::thread keyboard_th([&queue_keyboard]() {
        bool running = true;
        while (running) {
            std::string line;
            std::getline(std::cin, line);
            char c = line[0];
            if (line.empty()) {
                c = 'h';
            }
            else if (line.size() > 1) {
                c = line[0];
            }
            if (c == 'q') {
                running = false;
            }
            //printf("c: 0x%x\n", c);
            queue_keyboard.push(c);
        }
        std::cout << "keyboard thread exit" << std::endl;
    });
    char event_c = 0;
    bool running = true;
    while (running) {
        if (!queue_keyboard.empty()) {
            event_c = queue_keyboard.front();
            queue_keyboard.pop();
        }
        else {
            event_c = 0;
        }
        /*
         * Radio Control Protocol
         */
        /*
         * Usage:
         *  - w : up
         *  - s : down
         *  - a : turn left
         *  - d : turn right
         *  - i : forward
         *  - k : backward
         *  - j : left
         *  - l : right
         *  - x : radio control button
         */
        //keyboard read
        switch (event_c) {
        case 'w':
            drone_service_rc_put_vertical(0, -1.0);
            break;
        case 's':
            drone_service_rc_put_vertical(0, 1.0);
            break;
        case 'a':
            drone_service_rc_put_heading(0, -1.0);
            break;
        case 'd':
            drone_service_rc_put_heading(0, 1.0);
            break;
        case 'i':
            drone_service_rc_put_forward(0, -1.0);
            break;
        case 'k':
            drone_service_rc_put_forward(0, 1.0);
            break;
        case 'j':
            drone_service_rc_put_horizontal(0, -1.0);
            break;
        case 'l':
            drone_service_rc_put_horizontal(0, 1.0);
            break;
        case 'x':
            drone_service_rc_put_radio_control_button(0, 1);
            break;
        case 'p':
            {
                double x, y, z;
                drone_service_rc_get_position(0, &x, &y, &z);
                std::cout << "position x=" << std::fixed << std::setprecision(1) << x << " y=" << y << " z=" << z << std::endl;
            }
            break;
        case 'r':
            {
                double x, y, z;
                drone_service_rc_get_attitude(0, &x, &y, &z);
                std::cout << "attitude roll=" << std::fixed << std::setprecision(1) << x << " pitch=" << y << " yaw=" << z << std::endl;
            }
            break;
        case 't':
            std::cout << "simtime usec: " << drone_service_rc_get_time_usec(0) << std::endl;
            break;
        case 'q':
            std::cout << "quit" << std::endl;
            running = false;
            break;
        case 0:
            break;
        default:
            std::cout  << " ----- USAGE -----" << std::endl;
            std::cout  << " ----- STICK -----" << std::endl;
            std::cout  << "|  LEFT  | RIGHT  |" << std::endl;
            std:: cout << "|   w    |   i    |" << std::endl;
            std:: cout << "| a   d  | j   l  |" << std::endl;
            std:: cout << "|   s    |   k    |" << std::endl;
            std::cout  << " ---- BUTTON ----" << std::endl;
            std::cout  << " x : radio control button" << std::endl;
            std::cout  << " p : get position" << std::endl;
            std::cout  << " r : get attitude" << std::endl;
            break;
        }
        drone_service_rc_run();
        static double prev_x = 0.0;
        static double prev_y = 0.0;
        static double prev_z = 0.0;
        double x, y, z;
        drone_service_rc_get_position(0, &x, &y, &z);
        if (fabs(x - prev_x) > 0.1 || fabs(y - prev_y) > 0.1 || fabs(z - prev_z) > 0.1) {
            std::cout << "position x=" << std::fixed << std::setprecision(1) << x << " y=" << y << " z=" << z << std::endl;
            prev_x = x;
            prev_y = y;
            prev_z = z;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(real_sleep_msec));
    }

    /*
     * Stop service
     */
    drone_service_rc_stop();
    keyboard_th.join();
    return 0;
}