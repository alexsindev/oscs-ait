function Greetings(props) {
  return (
    <>
        <div>Greetings</div>
        <p>Hello { props.name } </p>
        <p>This is a { props.type } </p>
    </>
  )
}

Greetings.propTypes = {}

export default Greetings
