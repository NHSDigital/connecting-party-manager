import React, { useState } from "react";
import ProductCreationFlow from "./components/ProductCreationFlow";
import ProductSearch from "./components/ProductSearchFlow";

function App() {
  const [currentFlow, setCurrentFlow] = useState<"creation" | "search" | null>(
    null
  );

  const renderFlow = () => {
    switch (currentFlow) {
      case "creation":
        return <ProductCreationFlow />;
      case "search":
        return <ProductSearch />;
      default:
        return (
          <div className="min-h-screen flex flex-col items-center justify-center">
            <h1 className="text-2xl font-bold mb-6">
              Welcome to NHS Product Management
            </h1>
            <div className="flex space-x-4">
              <button
                className="nhs-button nhs-button-primary"
                onClick={() => setCurrentFlow("creation")}
              >
                Product Creation Flow
              </button>
              <button
                className="nhs-button nhs-button-primary"
                onClick={() => setCurrentFlow("search")}
              >
                Product Search Flow
              </button>
            </div>
          </div>
        );
    }
  };

  return <>{renderFlow()}</>;
}

export default App;
