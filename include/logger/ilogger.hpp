#pragma once

#include "logger/ilog.hpp"
#include "logger/ilog_file.hpp"


#include <vector>
#include <string>
#include <memory> 
#include <mutex> 
#include <atomic>  

namespace hako::logger {

typedef struct {
    ILog* log;
    std::unique_ptr<ILogFile> log_file;
} LogEntryType;

class IHakoLogger {
public:
    virtual ~IHakoLogger() = default;
    virtual std::vector<LogEntryType>& get_entries() = 0;
    virtual void add_entry(ILog& log, std::unique_ptr<ILogFile> log_file) = 0;
    virtual void run() = 0;
    virtual void flush() = 0;
    virtual void reset() = 0;
    virtual void close() = 0;

    static void set_time_usec(uint64_t t);
    static uint64_t get_time_usec();
    static void enable();
    static void disable();
    static bool enabled();
};

} // namespace hako::logger