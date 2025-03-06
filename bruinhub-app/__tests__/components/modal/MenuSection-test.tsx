import React from 'react';
import { render } from '@testing-library/react-native';
import MenuSection from '@/components/modal/MenuSection';

// Mock the componentStyles to ensure consistent testing
jest.mock('@/constants/componentStyles', () => ({
  componentStyles: {
    container: { padding: 10 },
    text: { fontSize: 16, fontWeight: 'bold' }
  }
}));

describe('MenuSection Component', () => {
  // Sample data for testing
  const mockSectionData = {
    name: 'Appetizers',
    items: [
      'Garlic Bread',
      'Caesar Salad',
      'Chicken Wings'
    ]
  };

  describe('Rendering', () => {
    it('renders section name correctly', () => {
      const { getByText } = render(<MenuSection {...mockSectionData} />);

      expect(getByText('Appetizers')).toBeTruthy();
    });

    it('renders all menu items', () => {
      const { getByText } = render(<MenuSection {...mockSectionData} />);

      expect(getByText('Garlic Bread')).toBeTruthy();
      expect(getByText('Caesar Salad')).toBeTruthy();
      expect(getByText('Chicken Wings')).toBeTruthy();
    });

    it('renders correct number of items', () => {
      const { getAllByText } = render(<MenuSection {...mockSectionData} />);

      const itemTexts = getAllByText(/Garlic Bread|Caesar Salad|Chicken Wings/);
      expect(itemTexts).toHaveLength(3);
    });
  });

  describe('Conditional Rendering', () => {
    it('handles long section name', () => {
      const longNameSection = {
        name: 'Extremely Long Section Name with Many Words',
        items: ['Single Item']
      };

      const { getByText } = render(<MenuSection {...longNameSection} />);

      expect(getByText('Extremely Long Section Name with Many Words')).toBeTruthy();
    });
  });

  describe('Styling', () => {
    it('applies correct styles to section name and items', () => {
      const { getByText } = render(<MenuSection {...mockSectionData} />);

      const sectionNameText = getByText('Appetizers');
      const firstItemText = getByText('Garlic Bread');

      expect(sectionNameText.props.style).toEqual(expect.objectContaining({
        fontSize: 16,
        fontWeight: 'bold'
      }));

      expect(firstItemText.props.style).toEqual(expect.objectContaining({
        fontSize: 16,
        fontWeight: 'bold'
      }));
    });
  });

  describe('Edge Cases', () => {
    it('handles special characters in section name and items', () => {
      const specialCharSection = {
        name: 'Special Characters & Symbols',
        items: [
          'Item with (Parentheses)',
          'Item with [Brackets]',
          'Item with $pecial Ch@r@cters'
        ]
      };

      const { getByText } = render(<MenuSection {...specialCharSection} />);

      expect(getByText('Special Characters & Symbols')).toBeTruthy();
      expect(getByText('Item with (Parentheses)')).toBeTruthy();
      expect(getByText('Item with [Brackets]')).toBeTruthy();
      expect(getByText('Item with $pecial Ch@r@cters')).toBeTruthy();
    });

    it('handles very long menu items', () => {
      const longItemsSection = {
        name: 'Verbose Section',
        items: [
          'Extremely Long Menu Item Description That Goes On And On And On',
          'Another Extremely Detailed Menu Item Description'
        ]
      };

      const { getByText } = render(<MenuSection {...longItemsSection} />);

      expect(getByText(/Extremely Long Menu Item Description/)).toBeTruthy();
      expect(getByText(/Another Extremely Detailed Menu Item/)).toBeTruthy();
    });
  });

  describe('Performance and Rendering', () => {
    it('renders multiple items efficiently', () => {
      const largeSection = {
        name: 'Large Section',
        items: Array.from({ length: 20 }, (_, i) => `Item ${i + 1}`)
      };

      const { getAllByText } = render(<MenuSection {...largeSection} />);

      const itemTexts = getAllByText(/Item \d+/);
      expect(itemTexts).toHaveLength(20);
    });
  });

  describe('Snapshot Testing', () => {
    it('matches snapshot', () => {
      const { toJSON } = render(<MenuSection {...mockSectionData} />);

      expect(toJSON()).toMatchSnapshot();
    });
  });
});