import React, { useState, ChangeEvent } from "react";

// =========== Interfaces ===========
interface Product {
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

interface ProductTeam {
  product_team_id: string;
  products: Product[];
}

interface SearchResult {
  org_code: string;
  product_teams: ProductTeam[];
}

interface ProductSearchResponse {
  results: SearchResult[];
}

interface EnvironmentConfig {
  environment: string;
  apiKey: string;
}

// =========== Component ===========
const ProductSearch: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [environmentConfig, setEnvironmentConfig] = useState<EnvironmentConfig>(
    {
      environment: "",
      apiKey: "",
    }
  );
  const [organisationCode, setOrganisationCode] = useState("");
  const [productTeamId, setProductTeamId] = useState("");
  const [
    searchResults,
    setSearchResults,
  ] = useState<ProductSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEnvironmentConfigEnabled =
    environmentConfig.environment.trim() !== "" &&
    environmentConfig.apiKey.trim() !== "";

  const handleSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams();
      if (organisationCode)
        queryParams.append("organisation_code", organisationCode);
      if (productTeamId) queryParams.append("product_team_id", productTeamId);

      const response = await fetch(
        `https://${
          environmentConfig.environment
        }.api.service.nhs.uk/connecting-party-manager/Product?${queryParams.toString()}`,
        {
          method: "GET",
          headers: {
            Authorization: "letmein",
            apikey: environmentConfig.apiKey,
            version: "1",
            "Content-Type": "application/json",
          },
        }
      );
      const responseData: ProductSearchResponse = await response.json();

      setSearchResults(responseData);
    } catch (err) {
      setError(`Failed to fetch search results. Please try again. ${err}`);
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
              <label className="nhs-label" htmlFor="organisation_code">
                Organisation Code
              </label>
              <input
                type="text"
                id="organisation_code"
                className="nhs-input"
                value={organisationCode}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setOrganisationCode(e.target.value)
                }
              />
            </div>

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
                onClick={handleSearch}
                disabled={loading}
                className="nhs-button nhs-button-primary"
              >
                {loading ? "Searching..." : "Search"}
              </button>
            </div>

            {searchResults && (
              <div className="mt-6">
                <h2 className="text-lg font-bold mb-4">Search Results</h2>
                {searchResults.results.map((result) => (
                  <div key={result.org_code} className="mb-4">
                    <h3 className="text-md font-bold">
                      Organisation Code: {result.org_code}
                    </h3>
                    {result.product_teams.map((team) => (
                      <div key={team.product_team_id} className="ml-4">
                        <h4 className="text-md font-bold">
                          Product Team ID: {team.product_team_id}
                        </h4>
                        <ul className="ml-4">
                          {team.products.map((product) => (
                            <li key={product.id} className="mb-2">
                              <p className="font-bold">
                                Product ID: {product.id}
                              </p>
                              <p>Name: {product.name}</p>
                              <p>ODS Code: {product.ods_code}</p>
                              <p>Status: {product.status}</p>
                              <p>Product Team Id: {product.product_team_id}</p>
                              <p>
                                Created On:{" "}
                                {new Date(product.created_on).toLocaleString()}
                              </p>
                              <p>
                                Updated On:{" "}
                                {product.updated_on
                                  ? new Date(
                                      product.updated_on
                                    ).toLocaleString()
                                  : "null"}
                              </p>
                              <p>
                                Deleted On:{" "}
                                {product.deleted_on
                                  ? new Date(
                                      product.deleted_on
                                    ).toLocaleString()
                                  : "null"}
                              </p>
                              <p>Keys: {product.keys}</p>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                ))}
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
          <span className="ml-2 text-lg">Product Search</span>
        </div>
      </header>

      <main className="nhs-main flex-grow">
        <h1 className="nhs-title">
          {currentStep === 0 ? "Configure Environment" : "Search for Products"}
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

export default ProductSearch;
