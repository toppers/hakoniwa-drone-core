#pragma once

#include <fstream>
#include <string>
#include <mutex>
#include <ctime>
#include <iomanip>
#include <sstream>

namespace hako::logger {
class DebugLogger {
public:
    // Singleton instance retrieval
    static DebugLogger& getInstance() {
        static DebugLogger instance;
        return instance;
    }

    // Initialize logger with a file path
    void initialize(const std::string& filePath) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (fileStream_.is_open()) {
            fileStream_.close();
        }
        fileStream_.open(filePath, std::ios::out | std::ios::trunc);
        if (!fileStream_) {
            throw std::runtime_error("Failed to open log file: " + filePath);
        }
        is_initialized_ = true;
    }

    // Log a message
    void log(const std::string& message) {
        if (!is_initialized_) {
            return;
        }
        std::lock_guard<std::mutex> lock(mutex_);
        if (!fileStream_.is_open()) {
            throw std::runtime_error("Logger is not initialized.");
        }

        fileStream_ << getCurrentTime() << " [DEBUG] " << message << std::endl;
    }
    // Flush
    void flush() {
        if (!is_initialized_) {
            return;
        }
        std::lock_guard<std::mutex> lock(mutex_);
        if (fileStream_.is_open()) {
            fileStream_.flush();
        }
    }
private:
    // Private constructor for singleton
    DebugLogger() = default;
    ~DebugLogger() {
        if (fileStream_.is_open()) {
            fileStream_.close();
        }
    }
    bool is_initialized_ = false;

    DebugLogger(const DebugLogger&) = delete;
    DebugLogger& operator=(const DebugLogger&) = delete;

    // Get current time as a string
    std::string getCurrentTime() {
        auto now = std::time(nullptr);
        std::ostringstream oss;
        oss << std::put_time(std::localtime(&now), "%Y-%m-%d %H:%M:%S");
        return oss.str();
    }

    std::ofstream fileStream_;
    std::mutex mutex_;
};
} // namespace hako::logger