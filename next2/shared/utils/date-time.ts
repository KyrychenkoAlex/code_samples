import { addMinutes, isAfter, format } from "date-fns";

export function getTimeIntervalsBetweenTwoDates(dateStart: Date, dateEnd: Date, intervalInMin: number = 60): Array <string>
{
  if (isAfter(dateStart, dateEnd)) {
    throw new Error('Date start cannot be more than date end!');
  }

  const timeRange: Array <string> = [];

  let dateStartInner = dateStart;

  while (!isAfter(dateStartInner, dateEnd)) {
    timeRange.push(format(dateStartInner, 'HH:mm'));
    dateStartInner = addMinutes(dateStartInner, intervalInMin);
  }

  return timeRange;
}
