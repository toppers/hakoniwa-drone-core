#pragma once

#include <string>
#include <vector>
#include <memory>
#include "ilog.hpp"

namespace hako::logger {

typedef enum {
    LOG_FILE_TYPE_CSV,
    LOG_FILE_TYPE_BINARY,
    LOG_FILE_TYPE_JSON,
    LOG_FILE_TYPE_NONE,
    LOG_FILE_TYPE_NUM
} LogFileType;

/**
 * Abstract interface for log file management.
 * Defines methods for writing, reading, flushing, and managing log data.
 */
class ILogFile {
public:
    static std::unique_ptr<ILogFile> create(LogFileType type, const std::string& file_name, const std::vector<LogHeaderType>& header);
    /**
     * Virtual destructor to ensure proper cleanup in derived classes.
     */
    virtual ~ILogFile() {}


    /**
     * Pure virtual method for setting the header information.
     * Must be implemented in derived classes.
     * @param header The header information for the log file.
     */
    virtual void load(const std::vector<LogHeaderType>& header) = 0;

    /**
     * Pure virtual method for writing log data.
     * Must be implemented in derived classes.
     * @param value Log data to be written.
     */
    virtual void write(const std::vector<LogDataType>& value) = 0;

    /**
     * Pure virtual method for flushing log data to the file.
     * Must be implemented in derived classes.
     */
    virtual void flush() = 0;

    /**
     * Pure virtual method for reading log data.
     * Must be implemented in derived classes.
     * @param value Output parameter to hold the read data.
     * @return True if reading was successful, false otherwise.
     */
    virtual bool read(std::vector<LogDataType>& value) = 0;

    /**
     * Pure virtual method for removing the last log entry.
     * Must be implemented in derived classes.
     */
    virtual void remove_last() = 0;

    /**
     * Pure virtual method for resetting the log file.
     * Must be implemented in derived classes.
     */
    virtual void reset() = 0;

protected:
    /**
     * Constructor for creating a new log file.
     * @param file_name The name of the file.
     * @param header The header information for the log file.
     */
    ILogFile(const std::string& file_name, const std::vector<LogHeaderType>& header) 
    {
        (void)file_name;
        (void)header;
    }

    /**
     * Constructor for loading an existing log file.
     * @param file_name The name of the file to load.
     */
    ILogFile(const std::string& file_name) {
        (void)file_name;
    }
};

} // namespace hako::logger

