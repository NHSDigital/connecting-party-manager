import { useState } from "react";
import ProductCreationFlow from "./components/ProductCreationFlow";
import ProductSearch from "./components/ProductSearchFlow";
import ProductDelete from "./components/ProductDeleteFlow";
import ProductTeamDelete from "./components/ProductDeleteTeamFlow";
import ProductRead from "./components/ProductReadFlow";

function App() {
  const [currentFlow, setCurrentFlow] = useState<
    | "creation"
    | "searchProducts"
    | "deleteProduct"
    | "deleteTeam"
    | "readProduct"
    | null
  >(null);

  const renderFlow = () => {
    switch (currentFlow) {
      case "creation":
        return <ProductCreationFlow />;
      case "searchProducts":
        return <ProductSearch />;
      case "deleteProduct":
        return <ProductDelete />;
      case "deleteTeam":
        return <ProductTeamDelete />;
      case "readProduct":
        return <ProductRead />;
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
                onClick={() => setCurrentFlow("searchProducts")}
              >
                Product Search Flow
              </button>
              <button
                className="nhs-button nhs-button-primary"
                onClick={() => setCurrentFlow("deleteProduct")}
              >
                Product Delete Flow
              </button>
              <button
                className="nhs-button nhs-button-primary"
                onClick={() => setCurrentFlow("deleteTeam")}
              >
                Product Team Delete Flow
              </button>
              <button
                className="nhs-button nhs-button-primary"
                onClick={() => setCurrentFlow("readProduct")}
              >
                Product Read Flow
              </button>
            </div>
          </div>
        );
    }
  };

  return <>{renderFlow()}</>;
}

export default App;
