import React, { Component } from 'react';
import PropTypes from 'prop-types';
import api from '../api/Api';

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
      showDelete: false
    };
  }
  goTo = (url) => {
    window.location.href = url;
  }
  toggleDelete = () => {
    this.setState({showDelete: true});
    // reset delete confimartion
    setTimeout(() => {
      this.setState({showDelete: false});
    }, 3000);
  }
  deleteInstance = () => {
    api.destroy('/counter/transfer/api/delete/' + this.props.instance.id + '/')
    .then((response) => {
      window.location.reload();
    })
    .catch((error) => {
      console.error(error);
    });
  }
  render() {
    var instance = { ...this.props.instance };
    return (
      <tr>
        <td className="cursor-pointer" onClick={ () => this.goTo(instance.view_url)}>{instance.date}</td>
        <td className="cursor-pointer" onClick={ () => this.goTo(instance.view_url)}>{instance.counter.name}</td>
        <td className="cursor-pointer" onClick={ () => this.goTo(instance.view_url)}>{instance.quantity}</td>
        <td className="cursor-pointer" onClick={ () => this.goTo(instance.view_url)}>{instance.worth}</td>
        <td className=" text-center">
          <ul className="icons-list">
            <li className="dropdown">
              { this.state.showDelete &&
                <button onClick={this.deleteInstance} type="button" aria-expanded="true" className="animated fadeIn btn btn-md bg-danger btn-primary dropdown-toggle legitRipple">
                Confirm Delete
              </button>
              }
              {!this.state.showDelete &&
                <button type="button" data-toggle="dropdown" aria-expanded="true" className="no-print animated fadeIn btn btn-md btn-primary dropdown-toggle legitRipple">
                Actions <span className="no-print  caret"></span>
                </button>
              }
              <ul className="dropdown-menu dropdown-menu-right">
                <li>
                  <a onClick={ () => this.goTo(instance.view_url)} href="javascript:;">
                     <i className="icon-eye"></i> View
                  </a>
                </li>
                <li>
                  <a onClick={ () => this.goTo(instance.update_items_url)} href="javascript:;">
                     <i className="icon-pencil"></i> EDIT
                  </a>
                </li>
                <li>
                  <a onClick={this.toggleDelete} href="javascript:;">
                    <i className=" icon-trash-alt"></i> DELETE
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </td>
    </tr>
    );
  }
}

TransferTableRow.propTypes = {
  instance: PropTypes.object.isRequired
};
export default TransferTableRow;
