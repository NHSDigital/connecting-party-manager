import React, { useState, ChangeEvent } from "react";

// =========== Interfaces ===========
interface ProductReadResponse {
  id: string;
  cpm_product_team_id: string;
  name: string;
  ods_code: string;
  status: string;
  created_on: string;
  updated_on: string | null;
  deleted_on: string | null;
  keys: any[];
}

interface EnvironmentConfig {
  environment: string;
  apiKey: string;
}

// =========== Component ===========
const ProductRead: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [environmentConfig, setEnvironmentConfig] = useState<EnvironmentConfig>(
    {
      environment: "",
      apiKey: "",
    }
  );
  const [productId, setProductId] = useState("");
  const [readResults, setReadResults] = useState<ProductReadResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEnvironmentConfigEnabled =
    environmentConfig.environment.trim() !== "" &&
    environmentConfig.apiKey.trim() !== "";

  const handleRead = async () => {
    setLoading(true);
    setError(null);

    try {
      // const response = await fetch(
      //   `https://${
      //     environmentConfig.environment
      //   }.api.service.nhs.uk/connecting-party-manager/Product/${productId}`,
      //   {
      //     method: "GET",
      //     headers: {
      //       Authorization: "letmein",
      //       apikey: environmentConfig.apiKey,
      //       version: "1",
      //       "Content-Type": "application/json",
      //     },
      //   }
      // );
      // const responseData: ProductReadResponse = await response.json();

      const responseData: ProductReadResponse = {
        id: "P.33A-KJ4",
        cpm_product_team_id: "0a5f4e25-ecdf-489d-80cf-5bd02ee14db0",
        name: "My Great Product",
        ods_code: "F5H1R",
        status: "active",
        created_on: "2025-03-05T12:08:42.659073+00:00",
        updated_on: null,
        deleted_on: null,
        keys: [],
      };

      setReadResults(responseData);
    } catch (err) {
      setError(`Failed to fetch Product results. Please try again. ${err}`);
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
              <label className="nhs-label" htmlFor="product_id">
                Product ID
              </label>
              <input
                type="text"
                id="product_id"
                placeholder="P.33A-KJ4"
                className="nhs-input"
                value={productId}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setProductId(e.target.value)
                }
              />
            </div>

            <div className="flex justify-end mt-6">
              <button
                type="button"
                onClick={handleRead}
                disabled={loading}
                className="nhs-button nhs-button-primary"
              >
                {loading ? "Reading..." : "Read"}
              </button>
            </div>

            {readResults && (
              <div className="mt-6">
                <h2 className="text-lg font-bold mb-4">Read Results</h2>
                <p className="font-bold">Product ID: {readResults.id}</p>
                <p>Name: {readResults.name}</p>
                <p>ODS Code: {readResults.ods_code}</p>
                <p>Status: {readResults.status}</p>
                <p>CPM Product Team Id: {readResults.cpm_product_team_id}</p>
                <p>
                  Created On:{" "}
                  {new Date(readResults.created_on).toLocaleString()}
                </p>
                <p>
                  Updated On:{" "}
                  {readResults.updated_on
                    ? new Date(readResults.updated_on).toLocaleString()
                    : "null"}
                </p>
                <p>
                  Deleted On:{" "}
                  {readResults.deleted_on
                    ? new Date(readResults.deleted_on).toLocaleString()
                    : "null"}
                </p>
                <p>Keys: {readResults.keys}</p>
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
          <span className="ml-2 text-lg">Product Read</span>
        </div>
      </header>

      <main className="nhs-main flex-grow">
        <h1 className="nhs-title">
          {currentStep === 0 ? "Configure Environment" : "Read Product"}
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

export default ProductRead;
