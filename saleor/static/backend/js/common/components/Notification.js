import jGrowl from 'jgrowl';
componentDidMount() {
    try { jGrowl; } catch (error) {};
}
$.jGrowl('Please select Kitchen !', {
    header: 'Kitchen required',
    theme: 'bg-danger'
  });