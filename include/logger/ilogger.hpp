#pragma once

#include "logger/ilog.hpp"
#include "logger/ilog_file.hpp"
#include "config/drone_config_types.hpp"


#include <vector>
#include <string>
#include <memory> 
#include <mutex> 
#include <atomic>  

namespace hako::logger {

struct LogEntryType {
    ILog* log;
    std::unique_ptr<ILogFile> log_file;
    uint64_t last_write_usec{0};
    bool has_written{false};
};

class IHakoLogger {
public:
    virtual ~IHakoLogger() = default;
    virtual std::vector<LogEntryType>& get_entries() = 0;
    virtual void add_entry(ILog& log, std::unique_ptr<ILogFile> log_file) = 0;
    virtual void run() = 0;
    virtual void flush() = 0;
    virtual void reset() = 0;
    virtual void close() = 0;

    static std::shared_ptr<IHakoLogger> create(uint64_t interval_usec = 1000);

    static void set_time_usec(uint64_t t);
    static uint64_t get_time_usec();
    static void enable();
    static void disable();
    static bool enabled();
};

} // namespace hako::logger
