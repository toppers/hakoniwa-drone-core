#pragma once

#include "logger/ilogger.hpp"
#include <vector>
#include <string>
#include <memory>      // For smart pointers
#include <mutex>       // For thread safety
#include <atomic>      // For atomic operations
#include <stdexcept>   // For exceptions

namespace hako::logger::impl {

#define MAX_WRITE_COUNT 256

class HakoLogger : public IHakoLogger {
private:
    std::vector<LogEntryType> entries;
    int write_count;
    mutable std::mutex logger_mutex;
public:
    static std::atomic<bool> enable_flag;
    static std::atomic<uint64_t> time_usec;

public:
    HakoLogger() : write_count(0) {}

    virtual ~HakoLogger() override {
        close();
    }
    std::vector<LogEntryType>& get_entries() override {
        return entries;
    }
    void add_entry(ILog& log, std::unique_ptr<ILogFile> log_file) override {
        std::lock_guard<std::mutex> lock(logger_mutex);
        log_file->flush();
        entries.push_back({&log, std::move(log_file)});
    }

    void run() override {
        if (!enable_flag.load(std::memory_order_relaxed)) {
            return;
        }

        std::lock_guard<std::mutex> lock(logger_mutex);

        try {
            for (auto& entry : entries) {
                auto log_data = entry.log->log_data();
                entry.log_file->write(log_data);
            }

            if (++write_count >= MAX_WRITE_COUNT) {
                for (auto& entry : entries) {
                    entry.log_file->flush();
                }
                write_count = 0;
            }
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error during logging: ") + e.what());
        }
    }
    void flush() override {
        std::lock_guard<std::mutex> lock(logger_mutex);
        for (auto& entry : entries) {
            entry.log_file->flush();
        }
    }

    void reset() override {
        std::lock_guard<std::mutex> lock(logger_mutex);
        for (auto& entry : entries) {
            if (entry.log_file) {
                entry.log_file->reset();
                entry.log_file->flush();
            }
        }
        write_count = 0;
    }

    void close() override {
        std::lock_guard<std::mutex> lock(logger_mutex);
        for (auto& entry : entries) {
            if (entry.log_file) {
                entry.log_file->flush();
                entry.log_file.reset();
            }
        }
        entries.clear();
    }
};

} // namespace hako::logger::impl

