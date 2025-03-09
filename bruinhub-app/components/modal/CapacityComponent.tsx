import { StyleSheet, Text, View } from "react-native";
import { ProgressBar } from "react-native-paper";
import { Colors } from "@/constants/Colors";

interface CapacityComponentProps {
  percentage: number,
  variant?: "default" | "secondary";
};

export default function CapacityComponent({ percentage, variant = "default" }: CapacityComponentProps) {
  const roundedPercentage = Math.round(percentage * 100);
  return (
    <View style={[styles.container, variant === "secondary" && styles.compactContainer]}>
      <View style={styles.progressContainer}>
        <View style={styles.progressBarWrapper}>
          <ProgressBar
            animatedValue={percentage}
            visible={true}
            color={Colors.light.shade}
            style={[styles.progressBar, variant === "secondary" && styles.compactProgressBar]}
          />
        </View>
        <Text style={[styles.percentageText, variant === "secondary" && styles.compactPercentageText]}>{roundedPercentage}%</Text>
      </View>
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

  compactContainer: {
    backgroundColor: Colors.light.icon,
    width: "100%",
    paddingTop: 5,
    paddingBottom: 0,
  },

  title: {
    fontSize: 18,
    fontWeight: 500,
    paddingBottom: 5,
    textAlign: "left",
  },

  progressBar: {
    height: 20,
    borderRadius: 10,
    backgroundColor: Colors.light.icon,
    width: "100%",
  },

  compactProgressBar: {
    height: 15,
    borderRadius: 10,
    backgroundColor: Colors.dark.tint,
    width: "100%",
  },

  progressBarWrapper: {
    marginRight: 10,
    flex: 1,
  },

  progressContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },

  percentageText: {
    fontSize: 18,
    fontWeight: 400,
    textAlign: "right",
  },

  compactPercentageText: {
    fontSize: 14,
    fontWeight: 400,
    textAlign: "right",
    marginLeft: 5,
  },
});
