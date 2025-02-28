import { Text, View } from "react-native";
import { componentStyles } from "@/constants/componentStyles";

interface MenuSection {
  title: string;
  items: string[];
}

interface MenuComponentProps {
  sections: MenuSection[];
}

export default function MenuComponent({ sections }: MenuComponentProps) {
  return (
    <View style={componentStyles.container}>
      {sections.map((section, index) => (
        <View key={index} style={componentStyles.sectionContainer}>
          <Text style={componentStyles.header}>{section.title}</Text>
          {section.items.map((dish, dishIndex) => (
            <Text key={dishIndex} style={componentStyles.text}>
              {dish}
            </Text>
          ))}
        </View>
      ))}
    </View>
  );
}
