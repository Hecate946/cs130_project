import { Text, View, StyleSheet } from "react-native";
import { componentStyles } from "@/constants/componentStyles";
import { Colors } from "@/constants/Colors";

interface MenuComponentProps {
  sections: Record<string, string[]>;
}

export default function MenuComponent({ sections }: MenuComponentProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Menu</Text>
      {Object.entries(sections).map(([title, items], index) => (
        <View key={index} style={componentStyles.sectionContainer}>
          <Text style={componentStyles.header}>{title}</Text>
          {items.map((dish, dishIndex) => (
            <Text key={dishIndex} style={componentStyles.text}>
              {dish}
            </Text>
          ))}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
    backgroundColor: Colors.light.background,
    paddingTop: 10,
    paddingBottom: 20,
  },

  text: {
    fontSize: 24,
    textTransform: "uppercase",
    fontWeight: 600,
    paddingBottom: 10,
  },
});
