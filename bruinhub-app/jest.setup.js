global.FormData = class {
    append() {}
};

jest.mock("expo-font", () => ({
    loadAsync: jest.fn(),
    isLoaded: jest.fn(() => true), // Mock isLoaded to always return true
}));

jest.mock("expo-router", () => ({
    useRouter: () => ({ push: jest.fn() }), // Mock navigation
    Link: ({ children }) => children, // Render links as plain elements
}));
