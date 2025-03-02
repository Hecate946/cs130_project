import { Text, View } from "react-native";
import { componentStyles } from "@/constants/componentStyles";

interface HourSection {
  day: string;
  hours: string[];
}

interface HourComponentProps {
  schedule: HourSection[];
}

export default function HourComponent({ schedule }: HourComponentProps) {
  return (
    <View style={componentStyles.container}>
      {schedule.map((section, index) => (
        <View key={index} style={componentStyles.sectionContainer}>
          <Text style={componentStyles.header}>{section.day}</Text>
          {section.hours.length > 0 ? (
            section.hours.map((hour, hourIndex) => (
              <Text key={hourIndex} style={componentStyles.text}>
                {hour}
              </Text>
            ))
          ) : (
            <Text style={componentStyles.closed}>Closed</Text>
          )}
        </View>
      ))}
    </View>
  );
}