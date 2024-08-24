const { Planet } = ReactPlanet;

function PlanetMenu() {
  return (
    <Planet
      centerContent={
        <div
          style={{
            height: 100,
            width: 100,
            borderRadius: '50%',
            backgroundColor: '#1da8a4',
          }}
        />
      }
      autoClose
      orbitRadius={120}
      bounceOnClose
      bounceOnOpen
      rotation={105}
      // The size of the center button
      centerRadius={40}
    >
      <div
        style={{
          height: 70,
          width: 70,
          borderRadius: '50%',
          backgroundColor: '#fefefe',
        }}
      />
      <div
        style={{
          height: 70,
          width: 70,
          borderRadius: '50%',
          backgroundColor: '#fefefe',
        }}
      />
      <div
        style={{
          height: 70,
          width: 70,
          borderRadius: '50%',
          backgroundColor: '#fefefe',
        }}
      />
    </Planet>
  );
}

ReactDOM.render(<PlanetMenu />, document.getElementById('react-planet-root'));