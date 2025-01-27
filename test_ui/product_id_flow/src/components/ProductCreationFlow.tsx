import React, { useState, ChangeEvent } from "react";
import { CheckCircle2 } from "lucide-react";

// =========== Interfaces ===========
interface TeamFormData {
  ods_code: string;
  name: string;
}

interface ProductFormData {
  name: string;
}

interface EnvironmentConfig {
  environment: string;
  apiKey: string;
}

interface ProductTeamResponse {
  id: string;
  name: string;
  ods_code: string;
  status: string;
  created_on: string;
  updated_on: string | null;
  deleted_on: string | null;
  keys: any[];
}

interface ProductResponse {
  id: string;
  product_team_id: string;
  name: string;
  ods_code: string;
  status: string;
  created_on: string;
  updated_on: string | null;
  deleted_on: string | null;
  keys: any[];
}

// =========== Component Interfaces ===========
interface StepHeaderProps {
  currentStep: number;
}

interface EnvironmentConfigStepProps {
  environmentConfig: EnvironmentConfig;
  setEnvironmentConfig: (config: EnvironmentConfig) => void;
  setCurrentStep: (step: number) => void;
  isEnvironmentConfigEnabled: boolean;
}

interface ProductTeamStepProps {
  teamFormData: TeamFormData;
  setTeamFormData: (data: TeamFormData) => void;
  productTeamResponse: ProductTeamResponse | null;
  loading: boolean;
  handleCreateProductTeam: () => Promise<void>;
  setCurrentStep: (step: number) => void;
  isCreateTeamEnabled: boolean;
  isNextEnabled: boolean;
}

interface ProductStepProps {
  productFormData: ProductFormData;
  setProductFormData: (data: ProductFormData) => void;
  productResponse: ProductResponse | null;
  loading: boolean;
  handleCreateProduct: () => Promise<void>;
  isCreateProductEnabled: boolean;
}

// =========== Component Implementations ===========
const StepHeader: React.FC<StepHeaderProps> = ({ currentStep }) => {
  const getStepTitle = () => {
    switch (currentStep) {
      case 0:
        return "Environment Configuration";
      case 1:
        return "Product Team Creation";
      case 2:
        return "Product Creation";
      default:
        return "";
    }
  };

  return (
    <header className="nhs-header">
      <div className="max-w-4xl mx-auto flex items-center">
        <span className="text-2xl font-bold">NHS</span>
        <span className="ml-2 text-lg">{getStepTitle()}</span>
      </div>
    </header>
  );
};

const EnvironmentConfigStep: React.FC<EnvironmentConfigStepProps> = ({
  environmentConfig,
  setEnvironmentConfig,
  setCurrentStep,
  isEnvironmentConfigEnabled,
}) => (
  <div>
    <div className="nhs-form-group">
      <label className="nhs-label" htmlFor="environment">
        Environment
      </label>
      <input
        type="text"
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
        data-emphasis={isEnvironmentConfigEnabled}
        className="nhs-button nhs-button-primary"
      >
        Next
      </button>
    </div>
  </div>
);

const ProductTeamStep: React.FC<ProductTeamStepProps> = ({
  teamFormData,
  setTeamFormData,
  productTeamResponse,
  loading,
  handleCreateProductTeam,
  setCurrentStep,
  isCreateTeamEnabled,
  isNextEnabled,
}) => (
  <div>
    <div className="nhs-form-group">
      <label className="nhs-label" htmlFor="ods_code">
        ODS Code
      </label>
      {productTeamResponse ? (
        <p className="bg-gray-50 p-2 rounded">{productTeamResponse.ods_code}</p>
      ) : (
        <input
          type="text"
          id="ods_code"
          className="nhs-input"
          value={teamFormData.ods_code}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setTeamFormData({
              ...teamFormData,
              ods_code: e.target.value,
            })
          }
          disabled={loading}
        />
      )}
    </div>

    <div className="nhs-form-group">
      <label className="nhs-label" htmlFor="team_name">
        Team Name
      </label>
      {productTeamResponse ? (
        <p className="bg-gray-50 p-2 rounded">{productTeamResponse.name}</p>
      ) : (
        <input
          type="text"
          id="team_name"
          className="nhs-input"
          value={teamFormData.name}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setTeamFormData({ ...teamFormData, name: e.target.value })
          }
          disabled={loading}
        />
      )}
    </div>

    {productTeamResponse && (
      <div className="nhs-success-banner">
        <CheckCircle2 className="h-5 w-5 mr-2" />
        <p>Product Team created successfully</p>
      </div>
    )}

    <div className="flex justify-between mt-6">
      <button
        type="button"
        onClick={handleCreateProductTeam}
        disabled={
          !isCreateTeamEnabled || loading || productTeamResponse !== null
        }
        data-emphasis={isCreateTeamEnabled && !loading && !productTeamResponse}
        className="nhs-button nhs-button-primary"
      >
        {loading ? "Creating..." : "Create Product Team"}
      </button>

      <button
        type="button"
        onClick={() => setCurrentStep(2)}
        disabled={!isNextEnabled}
        data-emphasis={isNextEnabled}
        className="nhs-button nhs-button-primary"
      >
        Next
      </button>
    </div>

    {productTeamResponse && (
      <div className="nhs-response-data">
        <h3 className="text-lg font-bold mb-2">Response Data</h3>
        <pre>{JSON.stringify(productTeamResponse, null, 2)}</pre>
      </div>
    )}
  </div>
);

const ProductStep: React.FC<ProductStepProps> = ({
  productFormData,
  setProductFormData,
  productResponse,
  loading,
  handleCreateProduct,
  isCreateProductEnabled,
}) => (
  <div>
    <div className="nhs-form-group">
      <label className="nhs-label" htmlFor="product_name">
        Name
      </label>
      {productResponse ? (
        <p className="bg-gray-50 p-2 rounded">{productResponse.name}</p>
      ) : (
        <input
          type="text"
          id="product_name"
          className="nhs-input"
          value={productFormData.name}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setProductFormData({
              ...productFormData,
              name: e.target.value,
            })
          }
          disabled={loading}
        />
      )}
    </div>

    {productResponse && (
      <div className="nhs-success-banner">
        <CheckCircle2 className="h-5 w-5 mr-2" />
        <p>Product created successfully</p>
      </div>
    )}

    <div className="flex justify-between mt-6">
      <button
        type="button"
        onClick={handleCreateProduct}
        disabled={
          !isCreateProductEnabled || loading || productResponse !== null
        }
        data-emphasis={isCreateProductEnabled && !loading && !productResponse}
        className="nhs-button nhs-button-primary"
      >
        {loading ? "Creating..." : "Create Product"}
      </button>
    </div>

    {productResponse && (
      <div className="nhs-response-data">
        <h3 className="text-lg font-bold mb-2">Response Data</h3>
        <pre>{JSON.stringify(productResponse, null, 2)}</pre>
      </div>
    )}
  </div>
);

const ProductCreationFlow: React.FC = () => {
  // =========== State Management ===========
  const [currentStep, setCurrentStep] = useState(0);
  const [teamFormData, setTeamFormData] = useState<TeamFormData>({
    ods_code: "",
    name: "",
  });
  const [environmentConfig, setEnvironmentConfig] = useState<EnvironmentConfig>(
    {
      environment: "",
      apiKey: "",
    }
  );
  const [
    productTeamResponse,
    setProductTeamResponse,
  ] = useState<ProductTeamResponse | null>(null);
  const [productFormData, setProductFormData] = useState<ProductFormData>({
    name: "",
  });
  const [
    productResponse,
    setProductResponse,
  ] = useState<ProductResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // =========== Button State Calculations ===========
  const isEnvironmentConfigEnabled =
    environmentConfig.environment.trim() !== "" &&
    environmentConfig.apiKey.trim() !== "";
  const isCreateTeamEnabled =
    teamFormData.ods_code.trim() !== "" && teamFormData.name.trim() !== "";
  const isNextEnabled = productTeamResponse !== null;
  const isCreateProductEnabled = productFormData.name.trim() !== "";

  // =========== API Handlers ===========
  const handleCreateProductTeam = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        "https://internal-dev.api.service.nhs.uk/connecting-party-manager/ProductTeam",
        {
          method: "POST",
          headers: {
            Authorization: "letmein",
            apikey: environmentConfig.apiKey,
            version: "1",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ods_code: teamFormData.ods_code,
            name: teamFormData.name,
          }),
        }
      );

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(
          `HTTP error! status: ${response.status}, body: ${errorBody}`
        );
      }

      const responseData: ProductTeamResponse = await response.json();
      setProductTeamResponse(responseData);
    } catch (err) {
      setError("Failed to create Product Team. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `https://internal-${environmentConfig.environment}.api.service.nhs.uk/connecting-party-manager/ProductTeam/${productTeamResponse?.id}/Product`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            apikey: environmentConfig.apiKey,
            version: "1",
            Authorization: "letmein",
          },
          body: JSON.stringify({
            ods_code: teamFormData.ods_code,
            name: teamFormData.name,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to create Product Team");
      }

      const responseData: ProductResponse = await response.json();
      setProductResponse(responseData);
    } catch (err) {
      setError("Failed to create Product. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // =========== Step Content Renderer ===========
  const getStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <EnvironmentConfigStep
            environmentConfig={environmentConfig}
            setEnvironmentConfig={setEnvironmentConfig}
            setCurrentStep={setCurrentStep}
            isEnvironmentConfigEnabled={isEnvironmentConfigEnabled}
          />
        );
      case 1:
        return (
          <ProductTeamStep
            teamFormData={teamFormData}
            setTeamFormData={setTeamFormData}
            productTeamResponse={productTeamResponse}
            loading={loading}
            handleCreateProductTeam={handleCreateProductTeam}
            setCurrentStep={setCurrentStep}
            isCreateTeamEnabled={isCreateTeamEnabled}
            isNextEnabled={isNextEnabled}
          />
        );
      case 2:
        return (
          <ProductStep
            productFormData={productFormData}
            setProductFormData={setProductFormData}
            productResponse={productResponse}
            loading={loading}
            handleCreateProduct={handleCreateProduct}
            isCreateProductEnabled={isCreateProductEnabled}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <StepHeader currentStep={currentStep} />

      <main className="nhs-main flex-grow">
        <h1 className="nhs-title">
          {currentStep === 0
            ? "Configure Environment"
            : currentStep === 1
            ? "Create Product Team"
            : "Create Product"}
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

export default ProductCreationFlow;
