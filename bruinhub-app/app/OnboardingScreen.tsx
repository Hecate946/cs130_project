import AsyncStorage from "@react-native-async-storage/async-storage";
import { Link } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { Button, FAB } from "react-native-paper";
import { Colors } from "@/constants/Colors";
import * as Haptics from "expo-haptics";

import SelectableChip from "@/components/onboarding/SelectableChip";

interface OnboardingScreenProps {
  onFinish: () => void;
};

export default function OnboardingScreen({ onFinish }: OnboardingScreenProps) {

  const handleFinish = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy); // Light, Medium, Heavy
    await AsyncStorage.setItem("finishedOnboarding", "true");
    onFinish();
  };

  return (
    <View style={styles.container}>
      <Text>This is the onboarding screen</Text>
      <SelectableChip name="hello" />
      <View style={{ position: "absolute", bottom: 70 }}>
        <Link href="/" asChild>
          <Button
            style={styles.button}
            onPress={handleFinish}
            uppercase={true}
            mode="elevated"
            contentStyle={styles.buttonContent}
            labelStyle={styles.buttonLabel}
          >
            Let's Go
          </Button>
        </Link>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: Colors.light.background,
    width: "100%"
  },

  button: {
    backgroundColor: Colors.light.icon,
    borderRadius: 60,
  },

  buttonLabel: {
    fontSize: 18,
    color: Colors.light.text,
  },

  buttonContent: {
    height: 64,
    width: 180,
    justifyContent: "center",
    alignItems: "center",
  },
});
