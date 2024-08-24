console.log("React component script loaded");

const Planet = ReactPlanet.Planet;

function PlanetMenu() {
  console.log("Rendering PlanetMenu");

  const refreshData = () => {
    console.log("Refresh button clicked");
    if (window.Shiny) {
      window.Shiny.setInputValue("refresh", Math.random());
    }
  };

  return (
    <div style={{ border: '1px solid red', padding: '20px' }}>
      <h3>Debug: PlanetMenu Component</h3>
      <Planet
        centerContent={
          <div
            style={{
              height: 80,
              width: 80,
              borderRadius: '50%',
              backgroundColor: '#1da8a4',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              cursor: 'pointer',
            }}
          >
            <span style={{ fontSize: '24px', color: 'white' }}>Menu</span>
          </div>
        }
        autoClose
        orbitRadius={120}
        bounceOnClose
        bounceOnOpen
        rotation={105}
        centerRadius={40}
      >
        <div
          onClick={refreshData}
          style={{
            height: 70,
            width: 70,
            borderRadius: '50%',
            backgroundColor: '#fefefe',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            cursor: 'pointer',
          }}
        >
          <span>Refresh</span>
        </div>
      </Planet>
    </div>
  );
}

const rootElement = document.getElementById('react-planet-root');
if (rootElement) {
  console.log("Root element found, rendering PlanetMenu");
  ReactDOM.render(<PlanetMenu />, rootElement);
  console.log("Finished rendering PlanetMenu");
} else {
  console.error("Root element not found");
}