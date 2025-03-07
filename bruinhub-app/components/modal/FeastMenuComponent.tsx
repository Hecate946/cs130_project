import React from "react";
import { View, Text, FlatList, StyleSheet } from "react-native";
import { componentStyles } from "@/constants/componentStyles";

interface FeastMenuComponentProps {
  [key: string]: {
    image: string | null;
    items: string[];
  };
};

export default function FeastMenuComponent({ menuData }: FeastMenuComponentProps) {
  return (
    <View>
      <Text style={styles.text}>Menu</Text>
      <FlatList
        data={Object.entries(menuData)} // Convert object to array of [sectionTitle, sectionData]
        keyExtractor={([sectionTitle]) => sectionTitle}
        scrollEnabled={false}
        renderItem={({ item: [sectionTitle, sectionData] }) => (
          <View style={componentStyles.sectionContainer}>
            {sectionData.items.length > 0 && (
              <View>
                <Text style={componentStyles.header}>{sectionTitle}</Text>
                <FlatList
                  data={sectionData.items}
                  keyExtractor={(item, index) => `${sectionTitle}-${index}`}
                  renderItem={({ item }) => <Text style={componentStyles.text}>{item}</Text>}
                />
              </View>
            )}
          </View>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  text: {
    fontSize: 24,
    fontWeight: 600,
    paddingTop: 10,
  },
});
