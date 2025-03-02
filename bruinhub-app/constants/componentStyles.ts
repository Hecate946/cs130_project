import { StyleSheet } from "react-native";
import { Colors } from "@/constants/Colors";

export const componentStyles = StyleSheet.create({
  container: {
    width: "100%",
    backgroundColor: Colors.light.background,
  },

  sectionContainer: {
    marginBottom: 10,
  },

  header: {
    fontSize: 18,
    fontWeight: "500",
    marginBottom: 5,
    marginLeft: 10,
  },

  text: {
    fontSize: 16,
    fontWeight: "400",
    paddingLeft: 20,
  },

  closed: {
    fontSize: 16,
    fontWeight: "400",
    paddingLeft: 10,
    color: "red",
  },
});
