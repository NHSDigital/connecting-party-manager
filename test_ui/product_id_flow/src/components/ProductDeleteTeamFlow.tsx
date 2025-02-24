import React, { useState, ChangeEvent } from "react";

// =========== Interfaces ===========

interface EnvironmentConfig {
  environment: string;
  apiKey: string;
}

interface ProductDeleteTeamResponse {
  code: string;
  message: string;
}

// =========== Component ===========
const ProductTeamDelete: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [environmentConfig, setEnvironmentConfig] = useState<EnvironmentConfig>(
    {
      environment: "",
      apiKey: "",
    }
  );
  const [productTeamId, setProductTeamId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [
    productTeamDeleteResponse,
    setProductTeamDeleteResponse,
  ] = useState<ProductDeleteTeamResponse | null>(null);

  const isEnvironmentConfigEnabled =
    environmentConfig.environment.trim() !== "" &&
    environmentConfig.apiKey.trim() !== "";

  const handleDeleteTeam = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `https://${environmentConfig.environment}.api.service.nhs.uk/connecting-party-manager/ProductTeam/${productTeamId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: "letmein",
            apikey: environmentConfig.apiKey,
            version: "1",
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(
          `HTTP error! status: ${response.status}, body: ${errorBody}`
        );
      }

      const responseData = await response.json();
      setProductTeamDeleteResponse(responseData);
    } catch (err) {
      setError(
        `Failed to Delete. Please try again. ${productTeamDeleteResponse}`
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div>
            <div className="nhs-form-group">
              <label className="nhs-label" htmlFor="environment">
                Environment
              </label>
              <input
                type="text"
                placeholder="eg. internal-dev, internal-qa, ref, int"
                id="environment"
                className="nhs-input"
                value={environmentConfig.environment}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setEnvironmentConfig({
                    ...environmentConfig,
                    environment: e.target.value,
                  })
                }
              />
            </div>

            <div className="nhs-form-group">
              <label className="nhs-label" htmlFor="apiKey">
                API Key
              </label>
              <input
                type="password"
                id="apiKey"
                className="nhs-input"
                value={environmentConfig.apiKey}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setEnvironmentConfig({
                    ...environmentConfig,
                    apiKey: e.target.value,
                  })
                }
              />
            </div>

            <div className="flex justify-end mt-6">
              <button
                type="button"
                onClick={() => setCurrentStep(1)}
                disabled={!isEnvironmentConfigEnabled}
                className="nhs-button nhs-button-primary"
              >
                Next
              </button>
            </div>
          </div>
        );
      case 1:
        return (
          <div>
            <div className="nhs-form-group">
              <label className="nhs-label" htmlFor="product_team_id">
                Product Team ID
              </label>
              <input
                type="text"
                id="product_team_id"
                className="nhs-input"
                value={productTeamId}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setProductTeamId(e.target.value)
                }
              />
            </div>

            <div className="flex justify-end mt-6">
              <button
                type="button"
                onClick={handleDeleteTeam}
                disabled={loading}
                className="nhs-button nhs-button-primary"
              >
                {loading ? "Deleting..." : "Delete"}
              </button>
            </div>

            {productTeamDeleteResponse && (
              <div className="mt-6">
                <p>Code: {productTeamDeleteResponse.code}</p>
                <p>Message: {productTeamDeleteResponse.message}</p>
              </div>
            )}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="nhs-header">
        <div className="max-w-4xl mx-auto flex items-center">
          <span className="text-2xl font-bold">NHS</span>
          <span className="ml-2 text-lg">Product Team Delete</span>
        </div>
      </header>

      <main className="nhs-main flex-grow">
        <h1 className="nhs-title">
          {currentStep === 0
            ? "Configure Environment"
            : "Delete A Product Team"}
        </h1>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-600 p-4 mb-6 flex items-center text-red-800">
            <p>{error}</p>
          </div>
        )}

        {getStepContent()}
      </main>

      <footer className="nhs-footer">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center">
            <span className="font-bold">NHS</span>
            <span className="ml-2">© {new Date().getFullYear()}</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ProductTeamDelete;
