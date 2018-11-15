import React, { Component } from 'react';
import PropTypes from 'prop-types';
import '../css/accordion.scss';

import TransferList from './TransferList';

export class TransferSection extends Component {
  /*
   * This component list stock transfers in accordions
   * Props:
   *  instance: (Required) An object with stock transfer details
   *         Array of items to be rendered in transfered item table
   *  Usage: <TransferSection
   *            instance={object}
   *          />
   * */
  constructor(props) {
    super(props);
    this.state = {
      controlId: 'control',
      collapse: 'collapse'
    };
  }
  toggleAccordion = () => {
    var toggled = (this.state.collapse === 'collapse') ? 'show' : 'collapse';
    this.setState({ collapse: toggled });
  }
  componentWillMount() {
    this.setState({ controlId: '#control' + this.props.instance.id });
  }
  render() {
    var instance = { ...this.props.instance };
    return (
      <div className="panel panel-white">
            <div onClick={this.toggleAccordion} className="panel-heading">
                <h6 className="panel-title">
                    <a data-toggle="collapse" href={this.state.controlId}>
                    <span className="label border-left-danger label-striped">
                      <b>Shop: </b> {instance.counter.name}
                    </span>
                    &nbsp;&nbsp;&nbsp;
                    <span className="label border-left-primary label-striped">
                      <b>Quantity: </b> {instance.quantity}
                    </span>
                    &nbsp;&nbsp;&nbsp;
                    <span className="label border-left-warning label-striped">
                      <b>Worth: </b> {instance.worth}
                    </span>
                    &nbsp;&nbsp;&nbsp;
                    <span className="label border-left-indigo label-striped">
                      <b>Date: </b> {instance.date}
                    </span>
                    &nbsp;&nbsp;&nbsp;
                    </a>
                </h6>
                <div className="heading-elements" >
                    <ul className="icons-list">
                        <li className={'section open ' + this.state.collapse}>
                            <a></a>
                        </li>
                    </ul>
                </div>
            </div>
            <div id={'control' + this.props.instance.id} className={'animated fadeIn panel-collapse ' + this.state.collapse} aria-expanded="false" >
                <div className="panel-body">
                    <TransferList items={instance.counter_transfer_items} parent={instance.id}/>
                </div>
            </div>
        </div>
    );
  }
}

TransferSection.propTypes = {
  instance: PropTypes.object.isRequired
};
export default TransferSection;
