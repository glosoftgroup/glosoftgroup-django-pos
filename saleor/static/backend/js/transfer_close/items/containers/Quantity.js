import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import ReactTooltip from 'react-tooltip';
import Tooltip from 'react-tooltip-lite';
import api from '../api/Api';
import { fetchItems } from '../actions/action-items';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import jGrowl from 'jgrowl';

export class Quantity extends Component {
  constructor(props) {
    super(props);
    this.state = {
      qty: 1,
      maxQty: 0,
      isOpen: false,
      edit: false
    };
  }

  componentDidMount = () => {
    this.setState({
      qty: this.props.instance.qty,
      maxQty: this.props.instance.quantity + this.props.instance.qty
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
      this.setState({
        [e.target.name]: value
      });
    } else if (!this.isNumeric(value)) {
      $.jGrowl('Quantity must be a digit!', {
        header: 'Quantity field error',
        theme: 'bg-danger'
      });
      return;
    } else if (value < 0) {
      $.jGrowl('Quantity should be a positive number', {
        header: 'Quantity field error',
        theme: 'bg-danger'
      });
      return;
    } else {
      this.setState({
        [e.target.name]: value
      });
      this.setState({qty: value});
      this.props.getDeficit(value);
    }
  }

  handleSubmit = () => {
    // validate
    if (this.state.qty < this.props.instance.qty) {
      console.warn('reduce qty');
    } else if (this.state.qty > this.state.maxQty) {
      var msg = 'Transfer Quantity cannot be more than ' + this.state.maxQty + '!';
      $.jGrowl(msg, {
        header: 'Transfer Quantity error',
        theme: 'bg-danger'
      });
      return;
    }
    if (!this.isNumeric(this.state.qty)) {
      $.jGrowl('Quantity must be a digit!', {
        header: 'Transfer Quantity error',
        theme: 'bg-danger'
      });
      return;
    }
    var formData = new FormData();
    formData.append('qty', this.state.qty);
    formData.append('price', (this.props.instance.unit_price * this.state.qty));
    api.update('/counter/transfer/api/update/item/' + this.props.instance.id + '/', formData)
    .then((response) => {
      this.setState({isOpen: false});
      this.props.fetchItems();
    })
    .catch((error) => { console.log(error); });
  }

  toggleEdit = () => {
    this.setState({isOpen: !this.state.isOpen});
  }

  render() {
    return (
      <div className="row">
        <ToastContainer />
        <ReactTooltip place="bottom"/>
        <div onClick={this.toggleEdit} className="col-md-8">
          {!this.state.edit &&
          <Tooltip isOpen={this.state.isOpen} content={(
            <div>
              <div className="editableform" >
                <div className="control-group form-group">
                  <div className="editable-input">
                    <input value={this.state.qty} onChange={this.handleChange}
                    type="number" name="qty" className="form-control"
                    />
                  </div>
                  <div className="editable-buttons">
                    <button onClick={this.handleSubmit} type="submit" className="btn hidden btn-primary btn-icon editable-submit">
                      <i className="icon-check"></i>
                    </button>
                    <button onClick={this.toggleEdit} type="button" className="btn btn-default btn-icon editable-cancel">
                      <i className="icon-x"></i>
                    </button>
                  </div>
                  <div className="editable-error-block help-block hidden"></div>
                </div>
              </div>
            </div>
          )}
            className="target" tagName="span" eventToggle="onClick">
            <span data-tip="Edit quantity" className="edit-qty text-primary cursor-pointer">
              {this.state.qty}
            </span>
        </Tooltip>
          }
        </div>
        <div className="col-md-4 mt-5">
        {this.state.edit &&
         <span onClick={this.editInstance} className="animated zoomIn btn btn-sm btn-primary cursor-pointer">Save</span>
        }
        </div>
      </div>
    );
  }
}

Quantity.propTypes = {
  instance: PropTypes.array.isRequired,
  getDeficit: PropTypes.func.isRequired,
  updateCartItem: PropTypes.func.isRequired,
  fetchItems: PropTypes.func.isRequired
};

function mapStateToProps(state) {
  return {};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({fetchItems}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(Quantity);
