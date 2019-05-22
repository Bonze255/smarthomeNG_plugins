handlers:
        shng_s7_file:
        class: logging.handlers.TimedRotatingFileHandler
        formatter: shng_simple
        level: DEBUG
        utc: false
        when: midnight
        backupCount: 7
        filename: ./var/log/s7-details.log
        encoding: utf8
loggers:
    plugins.S7:
        handlers: [shng_s7_file]
        level: DEBUG