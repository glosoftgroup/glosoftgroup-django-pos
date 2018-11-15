import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import jGrowl from 'jgrowl';

export class Quantity extends Component {
  constructor(props) {
    super(props);
    this.state = {
      qty: 1,
      maxQty: 0
    };
  }
  componentDidUpdate(prevProps, prevState, snapshot) {
    this.props.cart.map(value => {
      if (value.id === this.props.instance.id) {
        if (value.qty !== this.state.qty) {
          if (value.qty > this.state.maxQty) {
            // cant exceed quantity in store
          } else {
            this.setState({qty: value.qty});
          }
        }
      }
    });
  }
  componentDidMount = () => {
    this.setState({
      qty: this.props.instance.qty,
      maxQty: this.props.instance.quantity
    });
    try { jGrowl; } catch (error) {};
  }
  isNumeric = (n) => {
    return !isNaN(parseFloat(n)) && isFinite(n);
  }
  handleChange = (e) => {
    // transfer qty should not exceed store qty
    var value = e.target.value;
    if (value === '') {
      // pass
    } else if (!this.isNumeric(value)) {
      $.jGrowl('Quantity must be a digit!', {
        header: 'Quantity field error',
        theme: 'bg-danger'
      });
      return;
    } else if (value < 1) {
      $.jGrowl('Quantity must more than one!', {
        header: 'Quantity field error',
        theme: 'bg-danger'
      });
      return;
    }
    if (value > this.state.maxQty) {
      var msg = this.props.instance.sku + ' has ' + this.state.maxQty + ' items remaining! You can not transfer more that.';
      $.jGrowl(msg, {
        header: 'Quantity error',
        theme: 'bg-danger'
      });
      return;
    }

    this.setState({
      [e.target.name]: value
    });
    var payload = Object.assign(this.props.instance);
    payload.qty = value;
    this.props.updateCartItem(payload);
  }

  render() {
    return (
      <div>
        <ToastContainer />
        <input value={this.state.qty} onChange={this.handleChange}
          type="number" name="qty" className="form-control"
        />
      </div>
    );
  }
}

Quantity.propTypes = {
  instance: PropTypes.array.isRequired,
  updateCartItem: PropTypes.func.isRequired,
  cart: PropTypes.array.isRequired
};

function mapStateToProps(state) {
  return {};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(Quantity);
