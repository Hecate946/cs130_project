import { StyleSheet } from "react-native";
import { Colors } from "@/constants/Colors";

export const componentStyles = StyleSheet.create({
  container: {
    width: "100%",
    backgroundColor: Colors.light.background,
    paddingTop: 20,
  },

  sectionContainer: {
    marginBottom: 20,
  },

  header: {
    fontSize: 18,
    textTransform: "uppercase",
    fontWeight: "600",
    marginBottom: 10,
  },

  text: {
    fontSize: 16,
    fontWeight: "400",
    paddingLeft: 10,
  },

  closed: {
    fontSize: 16,
    fontWeight: "400",
    paddingLeft: 10,
    color: "red",
  },
});
