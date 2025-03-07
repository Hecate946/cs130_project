import { useState, useEffect } from "react";
import { View, Text, StyleSheet } from "react-native";

interface OperatingHoursProps {
  hoursToday: string[],
}

export default function OperatingHoursComponent({ hoursToday }: OperatingHoursProps) {
  const [currentTime, setCurrentTime] = useState(getFormattedTime());

  useEffect(() => {
    setCurrentTime(getFormattedTime());
  }, []);

  const currentMinutes = timeToMinutes(currentTime);

  let nextOpenTime = null;
  let closingTime = -1;
  let isOpen = false;

  for (const range of hoursToday) {
    if (range === "Closed all day") {
      break;
    }

    const [start, end] = range.split(" - ");

    const endMinutes = end === "12:00am" ? 24 * 60 : timeToMinutes(end);
    const startMinutes = timeToMinutes(start);

    if (currentMinutes >= startMinutes && currentMinutes < endMinutes) {
      isOpen = true;
      closingTime = endMinutes;
      break;
    } else if (currentMinutes < startMinutes && nextOpenTime === null) {
      nextOpenTime = startMinutes;
    }
  }

  const statusMessage = isOpen
    ? closingTime === 24 * 60
      ? `Open until Midnight`
      : `Open until ${formatMinutesToTime(closingTime)}`
    : nextOpenTime !== null
    ? `Closed until ${formatMinutesToTime(nextOpenTime)}`
    : "Closed";

  return (
    <View style={styles.container}>
      <Text style={{ color: isOpen ? "green" : "red", fontWeight: "bold", fontSize: 20 }}>
        {statusMessage}
      </Text>
    </View>
  );
};

const getFormattedTime = () => {
  const now = new Date();
  return now.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).toLowerCase();
};

const timeToMinutes = (timeStr : string) => {
  const [time, period] = timeStr.split(/(am|pm)/);
  let [hours, minutes] = time.split(":").map(Number);
  if (period === "pm" && hours !== 12) hours += 12;
  if (period === "am" && hours === 12) hours = 0;
  return hours * 60 + (minutes || 0);
};

const formatMinutesToTime = (minutes : number) => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  const period = hours >= 12 ? "PM" : "AM";
  const formattedHours = hours % 12 || 12;
  return `${formattedHours}:${mins.toString().padStart(2, "0")}${period.toLowerCase()}`;
};

const styles = StyleSheet.create({
  container: {
    paddingTop: 10,
    paddingBottom: 10,
  },
});
