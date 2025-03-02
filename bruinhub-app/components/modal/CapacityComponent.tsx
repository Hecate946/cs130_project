import { StyleSheet, Text, View } from "react-native";
import { ProgressBar } from "react-native-paper";
import { Colors } from "@/constants/Colors";

interface CapacityComponentProps {
  percentage: number,
};

export default function CapacityComponent({ percentage }: CapacityComponentProps) {
  const roundedPercentage = Math.round(percentage * 100);
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Current Occupancy: {roundedPercentage}%</Text>
      <ProgressBar
        animatedValue={percentage}
        visible={true}
        color={Colors.light.shade}
        style={styles.progressBar}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.light.background,
    width: "100%",
    paddingTop: 5,
    paddingBottom: 15,
  },

  text: {
    fontSize: 16,
    fontWeight: "400",
    paddingBottom: 5,
    textAlign: "left",
  },

  progressBar: {
    height: 20,
    borderRadius: 10,
    width: "100%",
    backgroundColor: Colors.light.icon,
    // padding: 12, //TODO Padding makes the color go away.
  },
});
