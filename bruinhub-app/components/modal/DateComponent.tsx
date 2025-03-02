import { Text, StyleSheet } from "react-native";

interface DateFormatterProps {
  isoString: string;
}

export default function DateFormatter({ isoString }: DateFormatterProps) {
  const formattedDate = new Date(isoString + "Z").toLocaleString("en-US", { // "Z" added to explicitly convert from UTC
    timeZone: "America/Los_Angeles",
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });

  return <Text style={styles.description}>{formattedDate}</Text>;
}

const styles = StyleSheet.create({
  description: {
    textAlign: "left",
    fontSize: 16,
    fontStyle: "italic",
    marginLeft: 4,
  },
});
