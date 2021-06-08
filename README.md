# RP2040-Pico-RTC
A MicroPython library implementing time functions that directly access the RP2040's internal RTC memory registers

This library has only been lightly tested with a Raspberry Pi Pico.

### class rp2RTC:

    Raspberry Pi Pico RTC class - manages the internal RP2040 Real Time Clock
    
    ≡≡≡ Methods ≡≡≡
    setRTC(year, month, day, hour, minute, second):
        Sets the RP2040 internal RTC to a spectific date and time.
    
    localtime():
        Returns the time stored in the RP2040 internal RTC.
        
     __weekDay(year, month, day):
        Calculates the weekday. 0 = Sunday, 6 = Saturday.
        
    __isLeapYear(year):
        Calculates whether a given year is a leap year.
    
    __validDateTime(year, month, day, hour, minute, second):
        This method validates a set of date/time information.
    
    __rtc_running():
        Returns True if the RP2040 RTC is running
