import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';

type Hours = {
  [day: string]: string;
};

interface GymOperatingHoursComponentProps {
  regularHours: Hours;
  specialHours: { [date: string]: string };
}

export default function GymOperatingHoursComponent({ regularHours, specialHours }: GymOperatingHoursComponentProps) {
  const currentDate = new Date();
  const currentDay = currentDate.toLocaleString('en-US', { weekday: 'long' });
  const currentTime = getFormattedTime();
  const currentMinutes = timeToMinutes(currentTime);
  const [statusMessage, setStatusMessage] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isSpecial, setIsSpecial] = useState(false);

  const specialDateKey = currentDate.toISOString().split('T')[0];

  useEffect(() => {
    let hoursToday = "";
    let startMinutes = -1;
    let endMinutes = -1;

    if (specialHours[specialDateKey]) {
      setIsSpecial(true);
      let specialHoursToday = specialHours[specialDateKey];
      if (specialHoursToday === "CLOSED") {
        setIsOpen(false);
      } else {
        hoursToday = specialHoursToday;
        const [start, end] = hoursToday.split(" - ");
        startMinutes = timeToMinutes(start);
        endMinutes = getEndMinutes(end, startMinutes);
        setIsOpen(currentMinutes >= startMinutes && currentMinutes < endMinutes);
      }
    } else {
      hoursToday = regularHours[currentDay];
      const [start, end] = hoursToday.split(" - ");
      startMinutes = timeToMinutes(start);
      endMinutes = getEndMinutes(end, startMinutes);
      setIsOpen(currentMinutes >= startMinutes && currentMinutes < endMinutes);
    }

    if (isOpen) {
      setStatusMessage(`Open until ${formatMinutesToTime(endMinutes)}`);
    } else if (isSpecial && !isOpen) {
      setStatusMessage("Closed Today");
      setIsOpen(false);
    } else {
      setStatusMessage(`Closed until ${formatMinutesToTime(startMinutes)}`);
      setIsOpen(false);
    }
  }, [specialHours, regularHours, currentDay, currentMinutes, specialDateKey]);


  return (
    <View style={styles.container}>
      {isSpecial && <Text style={{ color: 'red', fontWeight: 'bold', fontSize: 18 }}>Special Hours: </Text>}
      <Text style={{ color: isOpen ? 'green' : 'red', fontWeight: 'bold', fontSize: 18 }}>
        {statusMessage}
      </Text>
    </View>
  );
}

const getFormattedTime = () => {
  const now = new Date();
  return now.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).toLowerCase();
};

const timeToMinutes = (timeStr: string) => {
  const match = timeStr.match(/(\d+):(\d+)\s?(AM|PM)/i);
  if (!match) return -1;

  let hours = parseInt(match[1], 10);
  const minutes = parseInt(match[2], 10);
  const period = match[3].toUpperCase();

  if (period === "PM" && hours !== 12) hours += 12;
  if (period === "AM" && hours === 12) hours = 0;

  return hours * 60 + minutes;
};

const formatMinutesToTime = (minutes: number, startMinutes?: number) => {
  let adjustedMinutes = minutes;
  if (startMinutes !== undefined && minutes < startMinutes) {
    adjustedMinutes += 24 * 60;
  }

  const totalHours = Math.floor(adjustedMinutes / 60);
  const hours = totalHours % 24;
  const mins = adjustedMinutes % 60;
  const period = hours >= 12 ? 'PM' : 'AM';
  const formattedHours = hours % 12 || 12;
  return `${formattedHours}:${mins.toString().padStart(2, '0')}${period.toLowerCase()}`;
};


const getEndMinutes = (end: string, startMinutes: number) => {
  let endMinutes = timeToMinutes(end);

  if (endMinutes < startMinutes) {
    endMinutes += 24 * 60;
  }

  return endMinutes;
};

const styles = StyleSheet.create({
  container: {
    paddingTop: 10,
    paddingBottom: 10,
  },
});
