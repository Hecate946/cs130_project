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
      {/*<Text style={styles.title}>Current Occupancy</Text>*/}
      <View style={styles.progressContainer}>
        <View style={styles.progressBarWrapper}>
          <ProgressBar
            animatedValue={percentage}
            visible={true}
            color={Colors.light.shade}
            style={styles.progressBar}
          />
        </View>
        <Text style={styles.percentageText}>{roundedPercentage}%</Text>
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
  }
});
