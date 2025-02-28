import { StyleSheet, Text, View } from "react-native";
import { ProgressBar } from "react-native-paper";
import { Colors } from "@/constants/Colors";

interface CapacityComponentProps {
  capacity: number,
  percentage: number,
};

export default function Divider({ capacity, percentage }: CapacityComponentProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}> Current Capacity: {capacity}</Text>
      <Text style={styles.text}> Current Percentage Full: {percentage*100}%</Text>
      <ProgressBar animatedValue={percentage} visible={true} color={Colors.light.shade} style={styles.progressBar} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.light.background,
    width: "100%",
    paddingTop: 30,
    paddingBottom: 20,
  },

  text: {
    fontSize: 16,
    textTransform: 'uppercase',
    fontWeight: "500",
    paddingBottom: 15,
  },

progressBar: {
    height: 20,
    borderRadius: 10,
    width: "100%",
    //padding: 12, //TODO Padding makes the color go away.
},
  
});
