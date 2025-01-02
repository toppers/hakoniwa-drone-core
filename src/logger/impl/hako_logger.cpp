#include "hako_logger.hpp"
#include "csv_log_file.hpp"
using namespace hako::logger;

std::atomic<bool> hako::logger::impl::HakoLogger::enable_flag{false};
std::atomic<uint64_t> hako::logger::impl::HakoLogger::time_usec{0};


std::unique_ptr<ILogFile> ILogFile::create(LogFileType type, const std::string& file_name, const std::vector<LogHeaderType>& header) {
    switch (type) {
    case LOG_FILE_TYPE_CSV:
        return std::make_unique<hako::logger::impl::CsvLogFile>(file_name, header);
    default:
        throw std::runtime_error("Binary log file type not implemented.");
    }
}

void hako::logger::IHakoLogger::set_time_usec(uint64_t t) {
    hako::logger::impl::HakoLogger::time_usec.store(t, std::memory_order_relaxed);
}

uint64_t hako::logger::IHakoLogger::get_time_usec() {
    return hako::logger::impl::HakoLogger::time_usec.load(std::memory_order_relaxed);
}

void hako::logger::IHakoLogger::enable() {
    hako::logger::impl::HakoLogger::enable_flag.store(true, std::memory_order_relaxed);
}

void hako::logger::IHakoLogger::disable() {
    hako::logger::impl::HakoLogger::enable_flag.store(false, std::memory_order_relaxed);
}