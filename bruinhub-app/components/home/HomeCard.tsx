import React from "react";
import { Card, Title, Paragraph, IconButton } from "react-native-paper";
import { Colors } from "@/constants/Colors";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import * as Haptics from "expo-haptics";
import { useState } from "react";
import CapacityComponent from "../modal/CapacityComponent";
import MaterialCommunityIcons from "react-native-vector-icons/MaterialCommunityIcons";


interface HomeCardProps {
  name: string,
  description: string | null,
  facilityData?: {
    capacity?: number;
    occupants?: number;
  };
  isPinned: boolean,
  pinCallback: () => void,
  onPress: () => void,
}

export default function HomeCard({ name, description, facilityData, isPinned, pinCallback, onPress }: HomeCardProps) {
  const capacity = facilityData?.capacity ?? 0;
  const occupants = facilityData?.occupants ?? 0;
  const occupancyPercentage = capacity > 0 ? occupants / capacity : 0;

  const handlePress = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    onPress();
  };

  return (
    <Card onPress={handlePress} style={styles.card}>
      <View style={styles.imageContainer}>
        {/* <Image source={{ uri: imageUrl }} style={styles.image} /> */}
        <TouchableOpacity onPress={pinCallback} testID="pin-button">
          <MaterialCommunityIcons
            name={isPinned ? "pin" : "pin-outline"}
            size={28}
            style={styles.pinButton}
          />
        </TouchableOpacity>
      </View>
      <View style={styles.content}>
        <Title style={[styles.title, { color: Colors.light.text }]}>{name}</Title>
        <Paragraph style={{ color: Colors.light.text }}>{description}</Paragraph>
        {capacity > 0 && (
        <CapacityComponent percentage={occupancyPercentage} variant={"secondary"} />
        )}
      </View>
    </Card>
  )
};

const styles = StyleSheet.create({
  card: {
    margin: 10,
    backgroundColor: Colors.light.icon,
    borderRadius: 25,
  },

  imageContainer: {
    height: 55,
    position: "relative",
    backgroundColor: Colors.light.shade,
    borderTopLeftRadius: 25,
    borderTopRightRadius: 25,
  },

  image: {
    width: "100%",
    height: "100%",
  },

  pinButton: {
    position: "absolute",
    top: 4,
    right: 4,
    padding: 10,
    color: Colors.light.background,
  },

  content: {
    padding: 20
  },

  title: {
    fontSize: 24,
    fontWeight: 400,
    lineHeight: 28,
  },

  description: {
    fontSize: 16,
    fontWeight: 300,
  },
}); 