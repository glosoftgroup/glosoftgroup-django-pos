import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import api from '../api/Api';
import { fetchItems } from '../actions/action-items';
import { addCartItem, deleteCartItem, updateCartItem } from '../actions/action-cart';

export class TransferTableRow extends Component {
  /*
   * This component list stock transfers in rows
   * Props:
   *  instance: (Required) An object with stock transfer details
   *         Array of items to be rendered in transfered item table
   *  Usage: <TransferTableRow
   *            instance={object}
   *          />
   * */
  constructor(props) {
    super(props);
    this.state = {
      controlId: 'control',
      collapse: 'collapse',
      description: '',
      deficit: 0,
      qty: 0,
      showDelete: false,
      checked: ''
    };
  }
  componentWillMount() {
    this.setState({
      deficit: this.props.instance.deficit,
      qty: this.props.instance.qty
    });
  }
  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.state.checked === 'checked') {
      if (this.props.cart.length === 0) {
        this.setState({checked: ''});
      }
    } else if (this.state.checked !== 'checked') {
      this.props.cart.map(obj => {
        if (obj.id === this.props.instance.id) {
          if (this.state.qty !== obj.qty) {
            obj.qty = this.state.qty;
            obj.deficit = this.state.deficit;
          }
          obj.description = this.state.description;
          this.setState({checked: 'checked'});
        }
      });
    }
  }
  goTo = (url) => {
    window.location.href = url;
  }
  toggleCheckBox = () => {
    var checked = (this.state.checked === '') ? 'checked' : '';
    this.setState({checked});
    var payload = { ...this.props.instance };
    payload.deficit = this.state.deficit;
    payload.description = this.state.description;
    payload.qty = this.state.qty;
    checked === 'checked' ? this.props.addCartItem(payload) : this.props.deleteCartItem(payload.id);
  }
  updateCart = (actualQuantity, deficit, description) => {
    var checked = 'add';
    this.setState({checked: 'checked'});
    var payload = { ...this.props.instance };
    this.props.cart.map((value) => {
      if (value.id === payload.id) {
        checked = 'update';
      }
    });
    payload.deficit = deficit;
    payload.description = description;
    payload.qty = actualQuantity;
    checked === 'add' ? this.props.addCartItem(payload) : this.props.updateCartItem(payload);
    // this.props.addCartItem(payload);
  }
  getDeficit = (actualQuantity) => {
    var instance = { ...this.props.instance };
    var deficit = actualQuantity - instance.qty;
    this.setState({deficit: deficit, qty: actualQuantity});
    this.updateCart(actualQuantity, deficit, this.state.description);
  }
  handleChange = (event) => {
    this.setState({description: event.target.value});
    this.updateCart(this.state.qty, this.state.deficit, event.target.value);
  }
  closeItem = (flag) => {
    // validate
    var closeDetails = {store: flag};
    var formData = new FormData();
    formData.append('close_details', JSON.stringify(closeDetails));
    formData.append('qty', this.state.qty);
    formData.append('deficit', this.state.deficit);
    formData.append('description', this.state.description);
    formData.append('price', this.props.instance.price);
    api.update('/counter/transfer/api/close/item/' + this.props.instance.id + '/', formData)
    .then((response) => {
      this.setState({isOpen: false});
      this.props.fetchItems();
    })
    .catch((error) => { console.log(error); });
  }
  render() {
    var instance = { ...this.props.instance };
    return (
      <tr>
        <td>
        {instance.closed &&
          <span className="text-size-small text-success">Closed</span>
        }
        {!instance.closed &&
          <span className="text-size-small text-primary">Open</span>
        }
        </td>
        <td>
          <span>
          {instance.productName}<br/>{instance.sku}
          </span>
        </td>
        <td>{instance.transferred_qty}</td>
        <td><span>{instance.sold}</span></td>
        <td>{instance.unit_price}</td>
        <td>{instance.qty}</td>
        <td>{this.state.deficit}</td>
        <td><span>{instance.description}</span></td>
        <td className="text-center hidden">
          {!instance.closed &&
          <span className="no-print">
          <a onClick={ () => this.closeItem(false)} href="javascript:;" className="label label-primary">Carry forward</a>
          &nbsp;&nbsp;
          <a onClick={ () => this.closeItem(true)} href="javascript:;" className="label label-success">Return to stock</a>
          </span>
          }
          {instance.closed &&
          <span className="text-success">Closed</span>
          }
        </td>
    </tr>
    );
  }
}

TransferTableRow.propTypes = {
  addCartItem: PropTypes.func.isRequired,
  cart: PropTypes.array.isRequired,
  deleteCartItem: PropTypes.func.isRequired,
  instance: PropTypes.object.isRequired,
  fetchItems: PropTypes.func.isRequired,
  updateCartItem: PropTypes.func.isRequired
};

function mapStateToProps(state) {
  return {cart: state.cart};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({fetchItems, addCartItem, deleteCartItem, updateCartItem}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(TransferTableRow);
