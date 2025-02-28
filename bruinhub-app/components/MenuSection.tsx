import { Text, View } from "react-native";
import { componentStyles } from "@/constants/componentStyles";

interface MenuSectionProps {
  name: string;
  items: string[]; //dishes
}

export default function MenuSection({ name, items }: MenuSectionProps) {
  return (
    <View style={componentStyles.container}>
      {/* station name like "Pizza Section" */}
      <Text style={componentStyles.text}>{name}</Text>

      {/* map the dishes */}
      {items.map((dish, index) => (
        <Text key={index} style={componentStyles.text}>
          {dish}
        </Text>
      ))}
    </View>
  );
}