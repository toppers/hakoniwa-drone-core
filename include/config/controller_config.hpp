#pragma once

#include <string>
#include <unordered_map>
#include <fstream>
#include <sstream>
#include <iostream>
#include <stdexcept>
#include <cstdlib>
#include <cmath>

#ifdef _WIN32
#include <cstdlib> // For _dupenv_s
#endif
namespace hako::controller::impl {

class HakoControllerParamLoader {
private:
    std::string param_file_path_;
public:
    std::string get_controller_param_filedata(std::string& filepath) {
        param_file_path_ = filepath;
        std::ifstream file(param_file_path_);
        if (!file.is_open()) {
            throw std::runtime_error("Failed to open file: " + filepath);
        }
        std::string filedata((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        return filedata;
    }

    HakoControllerParamLoader() {}
    HakoControllerParamLoader(const std::string& input) {
        loadParametersFromString(input);
    }

    void reload(const std::string& input) {
#ifdef HAKO_DEBUG_LOG
        std::cout << "Reloading parameters from string" << std::endl;
#endif
        loadParametersFromString(input);
    }

    double getParameter(const std::string& paramName) const {
        auto it = parameters.find(paramName);
        if (it != parameters.end()) {
#ifdef HAKO_DEBUG_LOG
            std::cout << paramName << ": " << it->second << std::endl;
#endif
            return it->second;
        } else {
            throw std::runtime_error("Parameter not found: " + paramName);
        }
    }
    int getParameterInteger(const std::string& paramName) const {
        auto it = parameters.find(paramName);
        if (it != parameters.end()) {
#ifdef HAKO_DEBUG_LOG
            std::cout << paramName << ": " << it->second << std::endl;
#endif
            return static_cast<int>(std::round(it->second));
        } else {
            std::cerr << "Parameter not found: " << paramName << std::endl;
            return -1;
        }
    }


private:
    std::unordered_map<std::string, double> parameters;

    void parseStream(std::istream& stream) {
        validateAndParseStream(stream);
        std::string line;
        while (std::getline(stream, line)) {
            if (line.empty() || line[0] == '#') {
                continue;
            }

            std::istringstream iss(line);
            std::string param;
            double value;
            if (iss >> param >> value) {
                parameters[param] = value;
            }
        }
    }

    void loadParametersFromString(const std::string& input) {
        std::istringstream iss(input);
        parameters.clear();
        parseStream(iss);
    }

    void validateAndParseStream(std::istream& stream) {
        std::string line;
        int lineNumber = 0;

        while (std::getline(stream, line)) {
            lineNumber++;

            if (line.empty() || line[0] == '#') {
                continue;
            }

            if (!validateLine(line)) {
                throw std::runtime_error("Invalid parameter format at line " + std::to_string(lineNumber) + ": " + line);
            }

            std::istringstream iss(line);
            std::string param;
            double value;
            iss >> param >> value;
            parameters[param] = value;
        }
    }

    bool validateLine(const std::string& line) const {
        std::istringstream iss(line);
        std::string param;
        double value;

        if (!(iss >> param >> value)) {
            return false;
        }

        std::string extra;
        if (iss >> extra) {
            return false;
        }

        return true;
    }
};

}
