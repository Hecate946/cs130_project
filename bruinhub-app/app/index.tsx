import { Text, View } from "react-native";
import { Link } from "expo-router";
import { ActivityIndicator, Button } from "react-native-paper";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useEffect, useState } from "react";
import HomeScreen from "./HomeScreen";
import OnboardingScreen from "./OnboardingScreen";

export default function Index() {
  const [hasSeenOnboarding, setHasSeenOnboarding] = useState<boolean | null>(null);

  useEffect(() => {
    const checkOnboarding = async () => {
      const seen = await AsyncStorage.getItem("finishedOnboarding");
      setHasSeenOnboarding(seen === "true");
    };
    checkOnboarding();
  }, []);

  if (hasSeenOnboarding === null) {
    return <ActivityIndicator size="large" animating={true} />
  }

  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {
        hasSeenOnboarding ? 
        <HomeScreen onFinish={() => setHasSeenOnboarding(false)}/> 
        : 
        <OnboardingScreen onFinish={() => setHasSeenOnboarding(true)} />
      }
    </View>
  );
}
