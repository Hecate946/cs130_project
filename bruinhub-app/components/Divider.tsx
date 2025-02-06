import { StyleSheet, Text, View } from "react-native";
import { Link } from "expo-router";
import { Button } from "react-native-paper";
import { Colors } from "@/constants/Colors";

interface DividerProps {
  name: string,
};

export default function Divider({ name }: DividerProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>{name}</Text>
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
  },
});
