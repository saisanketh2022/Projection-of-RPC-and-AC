import json
import datetime
from datetime import datetime
import math

#load the json file and read the sampleJson.json.
with open('./sampleJson.json', 'r') as jsonData:
    data = json.load(jsonData)

#function converting all the time units to minutes.  
def convertTime(expireTime):
    if expireTime["unit"] == "HOURLY":
        return expireTime['value'] * 60
    elif expireTime["unit"] == "DAILY" or expireTime['unit'] == "DAYS":
        return expireTime['value'] * 24 * 60
    elif expireTime["unit"] == "WEEKLY" or expireTime['unit'] == "WEEKS":
        return expireTime['value'] * 24 * 7 * 60
    elif expireTime["unit"] == "MONTHLY" or expireTime['unit'] == "MONTHS":
        return expireTime['value'] * 24 * 30 * 60
    elif expireTime["unit"] == "YEARLY" or expireTime['unit'] == "YEARS":
        return expireTime['value'] * 24 * 365 * 60
    else:
        return 0
    
#converting the string time to datetime object.
# def convertStrToInt(time):
#     hourMin = datetime.strptime(time, "%H:%M")
#     hours = int((hourMin.hour)) * 60
#     minutes = int(hourMin.minute)
#     return hours + minutes

#function converting time string to minutes format.
def convertStrToInt(time):
    hours, minutes = map(int, time.split(':'))
    total_minutes = hours * 60 + minutes
    return total_minutes

    

#function to give time difference
def time_difference(input_date):
    input_date = datetime.strptime(input_date, '%d:%m:%y %H:%M')
    current_time = datetime.now()
    time_diff =  input_date - current_time
    time_diff_minutes = int(time_diff.total_seconds() / 60)
    return time_diff_minutes


#funtion to convert recurrence time units into minutes 
def recToUnit(schedule):
    expire = {
        "unit": schedule["recurrence"],
        "value": schedule["repeatInterval"]["every"]
    }
    return convertTime(expire)
    

#function to calculate the number of projection count for the various protections and their schedules.
# def projectionCount(data, givenTime="04:04:24 11:00"):
def projectionCount(data):
    givenTime = 2000  # For testing, replace this with the actual given time
    print("givenTime: ", givenTime)
    scheduleCount = {}
    for protection in data["protections"]:
        protectType = protection['type']
        scheduleCount[protectType] = {}
        for schedule in protection["schedules"]:
            count = 0
            if 'activeTime' in schedule['schedule']:
                from_time = schedule['schedule']['activeTime']['activeFromTime']
                until_time = schedule['schedule']['activeTime']['activeUntilTime']
                delta = convertStrToInt(until_time) - convertStrToInt(from_time)

                # Case 1: givenTime is before the active time range
                if givenTime < convertStrToInt(from_time):
                    print(convertStrToInt(from_time), "  case 1 is active")
                    count = 0

                # Case 2: givenTime is after the active time range
                elif givenTime > delta:
                    # Sub-case: givenTime is within a single day
                    if givenTime < 1440:
                        print("case 2--i is active")
                        max = math.ceil(delta / recToUnit(schedule["schedule"]))
                        count = max
                    else:
                        print("case 2--ii is active")
                        days_multiple = math.floor(givenTime / 1440)
                        count_1 = days_multiple * math.ceil(delta / recToUnit(schedule["schedule"]))
                        remain = givenTime % 1440
                        if remain < convertStrToInt(from_time):
                            count = count_1
                        else:
                            count_2 = math.ceil((remain - convertStrToInt(from_time)) / recToUnit(schedule["schedule"]))
                            count = count_1 + count_2

                # Case 3: givenTime is within the active time range
                else:
                    print("given > expiry")
                    if convertTime(schedule['expireAfter']) > 1440:
                        print("case 3--i is active, exp > 24")
                        days_multiple = math.floor(schedule['expireAfter'] / 1440)
                        count_1 = days_multiple * math.ceil(delta / recToUnit(schedule["schedule"]))
                        remain = givenTime % 1440
                        if remain < convertStrToInt(from_time):
                            count = count_1
                        else:
                            count_2 = math.ceil((remain - convertStrToInt(from_time)) / recToUnit(schedule["schedule"]))
                            count = count_1 + count_2
                    else:
                        print("ele")
            # else:
            #     if givenTime and convertStrToInt(givenTime) < convertTime(schedule['expireAfter']):
            #         count = math.ceil((convertStrToInt(givenTime) - convertStrToInt(schedule['schedule']['startTime']))/ recToUnit(schedule["schedule"]))
            #     else:
            #         count = math.ceil((convertTime(schedule['expireAfter']) - convertStrToInt(schedule['schedule']['startTime']))/ recToUnit(schedule["schedule"]))
            #         scheduleCount[protectType][schedule['name']] = count
            scheduleCount[protectType][schedule['name']] = count

    print(json.dumps(scheduleCount, indent=4))
    
if __name__ ==  "__main__":
    projectionCount(data=data)