# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
#
#    Raspberry Pi Pico RP2040 RTC Library
#
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
#
# Adapted from code by DWiskow and danjperron:
#   - https://www.raspberrypi.org/forums/viewtopic.php?f=146&t=300275&p=1807232#p1810708
#   - https://www.raspberrypi.org/forums/viewtopic.php?f=146&t=300275&p=1807232#p1810679
#
# Also adapted from the Official Raspberry Pi Pico SDK:
#   - https://github.com/raspberrypi/pico-sdk/blob/afc10f3599c27147a6f34781b7102d86f58aa5f6/src/rp2_common/hardware_rtc/rtc.c
# 
# RP2040 Datasheet:
#   - Availible: https://datasheets.raspberrypi.org/rp2040/rp2040-datasheet.pdf
#   - Datasheet last accessed on June 4th 2021
#   - See section 4.8 for information about the pico's built in Real Time Clock
#     (RTC)
#   - Section 4.8.6 shows the RTC_BASE address (0x4005C000)
#   - Section 4.8.6 shows details of the RD2040 setup registers used to program
#     the RTC
#   - Section 4.8.4 notes that writing to RTC registers can take 2 clock
#     periods additional to the time it takes for the write to get to the
#     system clock. A delay is thus implemented after upating RTC registers.
#   - Also read section 2.1.2. on Atomic Register Access. Explanation of use of
#     atomic register access by danjperron: 
#     https://www.raspberrypi.org/forums/viewtopic.php?f=146&t=300275&p=1807232#p1811105
#
# IMPORTANT NOTES:
#   - The Raspberry Pi Pico has no backup battery. RTC settings will be lost if
#     power is lost.
#   - This library will not set bit #8 of CTRL Register 0x4005e00c to force 'no
#     leap year' for years divisible by 100. See RP2040 Datasheet section 4.8.6
#     for info on this CTRL bit.
#   - There are no provisions for concurrency / multiprocessing
#   - The Day Of The Week (DOTW) stored in the RP2040 register follows a format
#     of '1-Monday…0-Sunday ISO 8601 mod 7', while Micropython's utime library
#     follows a format of '0-6 for Mon-Sun'.
#   - There is no timezone information
#   - This library is largely incomplete, only lightly tested, and is provided
#     'as-is-where-is' with no warranties or guarantees of any kind whether
#     express or implied.
#
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

from machine import mem32
from machine import disable_irq
from machine import enable_irq

from utime import sleep_us

from math import floor


class rp2RTC:
    """
    Raspberry Pi Pico RTC class - manages the internal RP2040 Real Time Clock
    
    ≡≡≡ Methods ≡≡≡
    setRTC(year, month, day, hour, minute, second):
        Sets the RP2040 internal RTC to a spectific date and time.
    
    localtime():
        Returns the date and time stored in the RP2040 internal RTC.
        
     __weekDay(year, month, day):
        Calculates the weekday. 0 = Sunday, 6 = Saturday.
        
    __isLeapYear(year):
        Calculates whether a given year is a leap year.
    
    __validDateTime(year, month, day, hour, minute, second):
        This method validates a set of date/time information.
    
    __rtc_running():
        Returns True if the RP2040 RTC is running
    """
    
    # RP2040 RTC memory register constants
    __RTC_BASE_MEM = 0x4005c000
    __ATOMIC_BITMASK_SET = 0x2000

    # Legal date/time field values for RP2040 RTC
    __LEGAL_YEAR = range(4096)
    __LEGAL_MONTH = range(1,13)
    __LEGAL_DAY = range(1,32) # 1..[28,29,30,31], depending on the month
    __LEGAL_HOUR = range(24)
    __LEGAL_MINUTE = range(60)
    __LEGAL_SECOND = range(60)

    # Memory Address Offsets
    __RTC_CTRL_RTC_ACTIVE_BITS = 0x00000002
    
    __RTC_RTC_0_DOTW_BITS = 0x07000000
    __RTC_RTC_0_HOUR_BITS = 0x001f0000
    __RTC_RTC_0_MIN_BITS = 0x00003f00
    __RTC_RTC_0_SEC_BITS = 0x0000003f

    __RTC_RTC_1_YEAR_BITS = 0x00fff000
    __RTC_RTC_1_MONTH_BITS = 0x00000f00
    __RTC_RTC_1_DAY_BITS = 0x0000001f
    


    #def __new__(cls, *args, **kwargs):

    #def __init__(self):
    
    def setRTC(self, year, month, day, hour, minute, second):        
        """
        Sets the RP2040 internal RTC to a spectific date and time.
        
        ≡≡≡ Required Parameters ≡≡≡
        year:   int, representing a valid year in the range of 0 - 4095
        month:  int, representing a valid month in the range of 1 - 12
        day:    int, representing a valid date in the range of 1..[28,29,30,31]
        hour:   int, representing a valid hour in the range of 0 - 23
        minute: int, representing a valid minute in the range of 0 - 59
        second: int, representing a valid second in the range of 0 - 59
        
        ≡≡≡ Raises ≡≡≡
        TypeError:  if the supplied parameter type is not an integer
        ValueError: if the supplied parameter is outside the legal range
        
        ≡≡≡ Returns ≡≡≡
        bool: True if successful, False if unsuccessful.
        """
        
        # Make sure RTC is running
        if not self.__rtc_running():
            return False
        
        # Error Checking. Raises TypeError or ValueError
        self.__validDateTime(self, year, month, day, hour, minute, second)

        # Get weekday
        wday = self.__weekDay(year, month, day)
        
        clkPeriod_us = 0
        
        try:
            # Find the period of one RTC clock cycle in microseconds
            clk_rtcDivider = (mem32[self.__RTC_BASE_MEM] & 0xffff) + 1 
            clkPeriod_us = int(1000000 / clk_rtcDivider)
            
            # Enter critical section
            irqState = disable_irq() 

            # Store date information to RTC registers
            mem32[self.__RTC_BASE_MEM + 4] = (year << 12) | (month  << 8) | day
            mem32[self.__RTC_BASE_MEM + 8] = ((hour << 16) | (minute << 8) | second) | (wday << 24)

            # Set the LOAD bit in the CTRL register
            mem32[self.__RTC_BASE_MEM + self.__ATOMIC_BITMASK_SET + 0xc] = 0x10

        except:
            raise

        finally:
            # End critical section
            enable_irq(irqState)
            
            # Writing to the RTC registers will take 2 clk_rtc clock periods to
            # arrive, additional to the clk_sys (system clock) domain, as per
            # RP2040 Datasheet Section 4.8.4.
            # Consequence: Reading localtime() too soon after updating the rtc
            # registers will return the date/time of the RTC clock prior to the
            # update.
            sleep_us(clkPeriod_us * 3)

        return True


    def localtime():
        """
        Returns the time stored in the RP2040 internal RTC.
        
        ≡≡≡ Returns ≡≡≡
        tuple: (year, month, day, hour, minute, second, dotw)
            year:   int, representing a year in the range of 0 - 4095
            month:  int, representing a month in the range of 1 - 12
            day:    int, representing a date in the range of 1 - 31
            hour:   int, representing a hour in the range of 0 - 23
            minute: int, representing a minute in the range of 0 - 59
            second: int, representing a second in the range of 0 - 59
            dotw:   int, representing the weekday (0 = Sun, 6 = Sat)
        
        bool: False if the onboard RTC is not running.
        """
        
        # Make sure RTC is running
        if not self.__rtc_running():
            return False
 
        # Note: RTC_0 should be read before RTC_1
        rtc_0 = mem32[self.__RTC_BASE_MEM + 0x1c]
        rtc_1 = mem32[self.__RTC_BASE_MEM + 0x18]         
 
        dotw = (rtc_0 & self.__RTC_RTC_0_DOTW_BITS ) >> 24
        hour = (rtc_0 & self.__RTC_RTC_0_HOUR_BITS ) >> 16
        minute = (rtc_0 & self.__RTC_RTC_0_MIN_BITS ) >> 8
        second = (rtc_0 & self.__RTC_RTC_0_SEC_BITS ) >> 0
        year = (rtc_1 & self.__RTC_RTC_1_YEAR_BITS ) >> 12
        month = (rtc_1 & self.__RTC_RTC_1_MONTH_BITS) >> 8
        day = (rtc_1 & self.__RTC_RTC_1_DAY_BITS ) >> 0

        return (year, month, day, hour, minute, second, dotw)
    
    
    
    def __weekDay(self, year, month, day):
        """
        Calculates the weekday. 0 = Sunday, 6 = Saturday.
        
        ≡≡≡ Required Parameters ≡≡≡
        year:   int, representing a valid year
        month:  int, representing a valid month in the range of 1 - 12
        day:    int, representing a valid date in the range of 1..[28,29,30,31]
        
        ≡≡≡ Returns ≡≡≡
        int: represents the weekday where 0 = Sunday, 6 = Saturday.
        """
        # Doomsday dates by month
        doomsdays = [3, 28, 14, 4, 9, 6, 11, 8, 5, 10, 7, 12] 
        if self.__isLeapYear(year):
            doomsdays[0] = 4
            doomsdays[1] = 29
        
        # The year's anchor day for each doomsday
        anchorDay = 2 + year + floor(year/4) - floor(year/100) + floor(year/400)

        dayOfWeek = (day - doomsdays[month-1] + anchorDay) % 7
        
        return dayOfWeek


    def __isLeapYear(self, year):
        """
        Calculates whether a given year is a leap year.
        
        ≡≡≡ Required Parameters ≡≡≡
        year:   int, representing a valid 4-digit year
        
        ≡≡≡ Returns ≡≡≡
        bool: True = is a leap year, False = is not a leap year
        """
        if year % 4 == 0 and year % 100 != 0:
            return True
        elif year % 400 == 0:
            return True
        else:
            return False


    def __validDateTime(self, year, month, day, hour, minute, second):
        """
        This method validates a set of date/time information.
        
        ≡≡≡ Required Parameters ≡≡≡
        year:   int, representing a valid year in the range of 0 - 4095
        month:  int, representing a valid month in the range of 1 - 12
        day:    int, representing a valid date in the range of 1..[28,29,30,31]
        hour:   int, representing a valid hour in the range of 0 - 23
        minute: int, representing a valid minute in the range of 0 - 59
        second: int, representing a valid second in the range of 0 - 59
        
        ≡≡≡ Raises ≡≡≡
        TypeError:  if the supplied parameter type is not an integer
        ValueError: if the supplied parameter is outside the legal range
        
        ≡≡≡ Returns ≡≡≡
        bool: True if the data types and values are legal
        """
        parameters = {'year'   : (year, self.__LEGAL_YEAR),
                      'month'  : (month, self.__LEGAL_MONTH),
                      'day'    : (day, self.__LEGAL_DAY),
                      'hour'   : (hour, self.__LEGAL_HOUR),
                      'minute' : (minute, self.__LEGAL_MINUTE),
                      'second' : (second, self.__LEGAL_SECOND)
                      }


        # Check if inputs are integers
        for key in parameters:
            if not isinstance(parameters[key][0], int):
                raise TypeError('Parameter ' +
                                key +
                                ' received parameter of type ' +
                                str(type(parameters[key][0])) +
                                ' - expected parameter of type \'int\'.')


        # Check if inputs are valid integers
        err = False
        errMin = 0
        errMax = 0

        for key in parameters:
            
            # Check the 'day' parameter
            if key == 'day':
                # If month is not valid, allow it to fail when processing its
                # own key
                if parameters['month'][0] not in parameters['month'][1]:
                    break
                
                # Months with 30 days:
                elif parameters['month'][0] in [4,6,9,11] and parameters[key][0] not in range(1,31):
                    err = True
                    errMin = 1
                    errMax = 30
                
                # February:
                elif parameters['month'][0] == 2 and parameters[key][0] not in range(1,29):                  
                    errMin = 1
                    if self.__isLeapYear(parameters['year'][0]):
                        errMax = 29
                    else:
                        errMax = 28
                    
                    if parameters[key][0] not in range(1,errMax + 1):
                       err = True 
                
                # Months with 31 days:
                elif parameters[key][0] not in range(1,32):
                    err = True
                    errMin = 1
                    errMax = 31
                
                    
            # Check all parameters other than 'day'
            elif parameters[key][0] not in parameters[key][1]:
                err = True
                errMin = min(parameters[key][1])
                errMax = max(parameters[key][1])
                
            if err:
                errMsg = ('Parameter \'' +
                          key +
                          '\' received value of ' +
                          str(parameters[key][0]) +
                          ' - must supply an integer from ' +
                          str(errMin) +
                          ' to ' +
                          str(errMax) +
                          ' inclusive')
                
                if key == 'day':
                    errMsg += ' for month ' + str(parameters['month'][0])
                              
                raise ValueError(errMsg)


    
    def __rtc_running(self):
        """Returns True if the RP2040 RTC is running
        
        ≡≡≡ Returns ≡≡≡
        bool: True if the RP2040 RTC is running, False if it is not running
        """
        ctrlRegister = mem32[self.__RTC_BASE_MEM + 0x0c]
        if (ctrlRegister & self.__RTC_CTRL_RTC_ACTIVE_BITS) > 0:
            return True
        else:
            return False
