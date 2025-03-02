import { Text, View } from "react-native";
import { componentStyles } from "@/constants/componentStyles";

interface MenuSectionProps {
  name: string;
  items: string[];
}

export default function MenuSection({ name, items }: MenuSectionProps) {
  return (
    <View style={componentStyles.container}>
      <Text style={componentStyles.text}>{name}</Text>

      {items.map((dish, index) => (
        <Text key={index} style={componentStyles.text}>
          {dish}
        </Text>
      ))}
    </View>
  );
}